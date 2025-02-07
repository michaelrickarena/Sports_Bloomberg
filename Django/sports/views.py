from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Moneyline, Overunder, Props, Scores, Spreads, UpcomingGames, latest_Moneyline, latest_Overunder, latest_Props, latest_Spreads, DistinctProps
from .serializers import (
    MoneylineSerializer,
    OverunderSerializer,
    PropsSerializer,
    ScoresSerializer,
    SpreadsSerializer,
    UpcomingGamesSerializer,
    latest_MoneylineSerializer,
    latest_OverunderSerializer,
    latest_PropsSerializer,
    latest_SpreadsSerializer,
    DistinctPropsSerializer
)
from rest_framework.pagination import PageNumberPagination
from .services import get_chart_data
from django.core.cache import cache
import logging
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
import stripe
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from dotenv import load_dotenv
import os
from django.views.decorators.csrf import csrf_exempt  # Import csrf_exempt decorator
import json
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from django.utils import timezone
from datetime import timedelta
from .models import UserSubscription
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.timezone import now
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed


load_dotenv()

STRIPE_DOMAIN = os.getenv('STRIPE_DOMAIN')


logger = logging.getLogger("logsport")

class MoneylineListView(APIView):
    def get(self, request):
        game_id = request.query_params.get('game_id')  # Use 'game_id' to match the database column
        page_number = request.query_params.get('page', 1)  # Get the page number from the query params
        cache_key = f'moneyline_data_{game_id}_page_{page_number}'  # Cache key specific to game_id and page

        # Check cache first
        data = cache.get(cache_key)
        if not data:
            if game_id:
                moneylines = Moneyline.objects.filter(game_id=game_id).order_by('last_updated_timestamp')  # Filter by game_id and order by 'last_updated_timestamp'
            else:
                moneylines = Moneyline.objects.all().order_by('last_updated_timestamp')  # Fallback if no game_id is provided

            paginator = PageNumberPagination()
            paginator.page_size = 250
            result_page = paginator.paginate_queryset(moneylines, request)
            serializer = MoneylineSerializer(result_page, many=True)
            data = paginator.get_paginated_response(serializer.data).data
            cache.set(cache_key, data, timeout=7200)  # Cache the result for 2 hours

        return Response(data)  # Return the cached or fresh data

class OverunderListView(APIView):
    def get(self, request):
        game_id = request.query_params.get('game_id')
        sport_type = request.query_params.get('sport_type')
        page_number = request.query_params.get('page', 1)
        cache_key = f'overunder_data_{game_id}_{sport_type}_page_{page_number}'

        data = cache.get(cache_key)
        if not data:
            filters = {}
            if game_id:
                filters['game_id'] = game_id
            if sport_type:
                filters['sport_type'] = sport_type

            overunders = Overunder.objects.filter(**filters).order_by('last_updated_timestamp')

            paginator = PageNumberPagination()
            paginator.page_size = 250
            result_page = paginator.paginate_queryset(overunders, request)
            serializer = OverunderSerializer(result_page, many=True)
            data = paginator.get_paginated_response(serializer.data).data
            cache.set(cache_key, data, timeout=7200)

        return Response(data)


class SpreadsListView(APIView):
    def get(self, request):
        game_id = request.query_params.get('game_id')
        sport_type = request.query_params.get('sport_type')
        page_number = request.query_params.get('page', 1)
        cache_key = f'spreads_data_{game_id}_{sport_type}_page_{page_number}'

        data = cache.get(cache_key)
        if not data:
            filters = {}
            if game_id:
                filters['game_id'] = game_id
            if sport_type:
                filters['sport_type'] = sport_type

            spreads = Spreads.objects.filter(**filters).order_by('last_updated_timestamp')

            paginator = PageNumberPagination()
            paginator.page_size = 250
            result_page = paginator.paginate_queryset(spreads, request)
            serializer = SpreadsSerializer(result_page, many=True)
            data = paginator.get_paginated_response(serializer.data).data
            cache.set(cache_key, data, timeout=7200)

        return Response(data)


class PropsListView(APIView):
    def get(self, request):
        player_name = request.query_params.get('player_name')
        prop_type = request.query_params.get('prop_type')  # Added prop_type parameter
        page_number = request.query_params.get('page', 1)
        cache_key = f'props_data_{player_name}_{prop_type}_page_{page_number}'  # Updated cache key

        # Check cache first
        data = cache.get(cache_key)
        if not data:
            filters = {}
            if player_name:
                filters['player_name__icontains'] = player_name  # Partial match for player name
            if prop_type:
                filters['prop_type'] = prop_type  # Filter by prop_type

            # Fetch filtered props
            props = Props.objects.filter(**filters).order_by('last_updated_timestamp')

            paginator = PageNumberPagination()
            paginator.page_size = 250
            result_page = paginator.paginate_queryset(props, request)
            serializer = PropsSerializer(result_page, many=True)
            data = paginator.get_paginated_response(serializer.data).data
            cache.set(cache_key, data, timeout=7200)

        return Response(data)

# New View for Chart Data
class MoneylineChartDataView(APIView):
    def get(self, request):
        # Retrieve query parameters
        game_id = request.query_params.get('game_id')
        sport_type = request.query_params.get('sport_type')

        try:
            # Apply filtering based on query parameters
            if game_id and sport_type:
                moneylines = Moneyline.objects.filter(game_id=game_id, sport_type=sport_type)
            elif game_id:
                moneylines = Moneyline.objects.filter(game_id=game_id)
            elif sport_type:
                moneylines = Moneyline.objects.filter(sport_type=sport_type)
            else:
                return Response(
                    {"error": "Please provide at least game_id or sport_type."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Serialize the data (assuming you want chart data for all matching records)
            serializer = MoneylineSerializer(moneylines, many=True)
            data = serializer.data

            return Response(data, status=status.HTTP_200_OK)

        except Moneyline.DoesNotExist:
            return Response(
                {"error": "No matching data found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PropsChartDataView(APIView):
    def get(self, request):
        game_id = request.query_params.get('game_id')
        sport_type = request.query_params.get('sport_type')
        player_name = request.query_params.get('player_name')

        try:
            filters = {}
            if game_id:
                filters['game_id'] = game_id
            if sport_type:
                filters['sport_type'] = sport_type
            if player_name:
                filters['player_name__icontains'] = player_name

            props = Props.objects.filter(**filters)

            # Serialize the data (assuming you want chart data for all matching records)
            serializer = PropsSerializer(props, many=True)
            data = serializer.data

            return Response(data, status=status.HTTP_200_OK)

        except Props.DoesNotExist:
            return Response(
                {"error": "No matching data found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class OverunderChartDataView(APIView):
    def get(self, request):
        game_id = request.query_params.get('game_id')
        sport_type = request.query_params.get('sport_type')

        try:
            filters = {}
            if game_id:
                filters['game_id'] = game_id
            if sport_type:
                filters['sport_type'] = sport_type

            overunders = Overunder.objects.filter(**filters)

            # Serialize the data (assuming you want chart data for all matching records)
            serializer = OverunderSerializer(overunders, many=True)
            data = serializer.data

            return Response(data, status=status.HTTP_200_OK)

        except Overunder.DoesNotExist:
            return Response(
                {"error": "No matching data found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SpreadsChartDataView(APIView):
    def get(self, request):
        game_id = request.query_params.get('game_id')
        sport_type = request.query_params.get('sport_type')

        try:
            filters = {}
            if game_id:
                filters['game_id'] = game_id
            if sport_type:
                filters['sport_type'] = sport_type

            spreads = Spreads.objects.filter(**filters)

            # Serialize the data (assuming you want chart data for all matching records)
            serializer = SpreadsSerializer(spreads, many=True)
            data = serializer.data

            return Response(data, status=status.HTTP_200_OK)

        except Spreads.DoesNotExist:
            return Response(
                {"error": "No matching data found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DistinctPropsListView(APIView):
    def get(self, request):
        sport_type = request.query_params.get('sport_type', None)  # Get sport_type from query params
        
        # Filter by sport_type if provided, otherwise return all results
        if sport_type:
            distinct_props = DistinctProps.objects.filter(sport_type=sport_type)
        else:
            distinct_props = DistinctProps.objects.all()

        # Paginate the results
        paginator = PageNumberPagination()
        paginator.page_size = 100  # Adjust the number of results per page
        result_page = paginator.paginate_queryset(distinct_props, request)

        # Serialize the filtered results
        serializer = DistinctPropsSerializer(result_page, many=True)
        
        # Return the paginated response
        return paginator.get_paginated_response(serializer.data)


class ScoresListView(APIView):
    def get(self, request):
        scores = Scores.objects.all()
        paginator = PageNumberPagination()
        paginator.page_size = 250  # Limit the number of results per page
        result_page = paginator.paginate_queryset(scores, request)
        serializer = ScoresSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

class UpcomingGamesListView(APIView): 
    def get(self, request):
        # Get the sport_title from query parameters
        sport_title = request.query_params.get('sport_title', None)

        # Define the cache key, including sport_title if it exists
        cache_key = f"upcoming_games_{sport_title}" if sport_title else "upcoming_games_all"

        # Check if data is available in the cache
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info(f"Cache hit for {cache_key}.")
            return Response(cached_data)  # Return cached response

        # If not in cache, fetch data from the database
        logger.info(f"Cache miss for {cache_key}. Fetching from database.")
        
        # Apply filtering if sport_title is provided
        if sport_title:
            upcoming_games = UpcomingGames.objects.filter(sport_title=sport_title)
        else:
            upcoming_games = UpcomingGames.objects.all()

        # Serialize the data
        serializer = UpcomingGamesSerializer(upcoming_games, many=True)

        # Cache the result for 2 hours (7200 seconds)
        cache.set(cache_key, serializer.data, timeout=7200)
        logger.info(f"{cache_key} data cached.")

        return Response(serializer.data)


class latest_MoneylineListView(APIView):
    def get(self, request):
        # Get game_id from query parameters
        game_id = request.query_params.get("game_id")
        
        # Validate game_id is provided
        if not game_id:
            return Response(
                {"error": "game_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the data is cached
        cache_key = f"latest_moneyline_{game_id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            # Return cached data if available
            return Response(cached_data)

        # Filter the latest_moneyline table by game_id
        latest_moneyline = latest_Moneyline.objects.filter(game=game_id)[:10]  # Limit to 10 results

        # Paginate the results
        paginator = PageNumberPagination()
        paginator.page_size = 100
        result_page = paginator.paginate_queryset(latest_moneyline, request)

        # Serialize the results
        serializer = latest_MoneylineSerializer(result_page, many=True)

        # Cache the result for 10 minutes
        cache.set(cache_key, serializer.data, timeout=600)

        # Return the paginated response
        return paginator.get_paginated_response(serializer.data)

class latest_OverunderListView(APIView):
    def get(self, request):
        # Get game_id from query parameters
        game_id = request.query_params.get("game_id")
        
        # Check if game_id is provided and filter the latest_Overunder table accordingly
        if game_id:
            latest_overunders = latest_Overunder.objects.filter(game=game_id)
        else:
            latest_overunders = latest_Overunder.objects.all()
        
        # Paginate the results
        paginator = PageNumberPagination()
        paginator.page_size = 250  # Limit the number of results per page
        result_page = paginator.paginate_queryset(latest_overunders, request)
        
        # Serialize the results
        serializer = latest_OverunderSerializer(result_page, many=True)
        
        # Return the paginated response
        return paginator.get_paginated_response(serializer.data)


class latest_PropsListView(APIView):
    def get(self, request):
        # Get query parameters
        player_name = request.query_params.get('player_name', None)
        prop_type = request.query_params.get('prop_type', None)

        # Ensure player_name is provided
        if not player_name:
            return Response({"error": "player_name parameter is required"}, status=400)

        # Filter by player_name
        latest_props = latest_Props.objects.filter(player_name__icontains=player_name)

        # If prop_type is provided, filter further by prop_type
        if prop_type:
            latest_props = latest_props.filter(prop_type__icontains=prop_type)

            # Return all rows (full details) if both filters are applied
            serializer = latest_PropsSerializer(latest_props, many=True)
            return Response(serializer.data)

        # If only player_name is provided, return unique prop_types
        unique_prop_types = latest_props.values_list('prop_type', flat=True).distinct()

        # Paginate the results
        paginator = PageNumberPagination()
        paginator.page_size = 100
        result_page = paginator.paginate_queryset(unique_prop_types, request)

        # Return the paginated response
        return paginator.get_paginated_response(result_page)



class latest_SpreadsListView(APIView):
    def get(self, request):
        # Get game_id from query parameters
        game_id = request.query_params.get("game_id")
        
        # Check if game_id is provided and filter the latest_Spreads table accordingly
        if game_id:
            latest_spreads = latest_Spreads.objects.filter(game=game_id)
        else:
            latest_spreads = latest_Spreads.objects.all()
        
        # Paginate the results
        paginator = PageNumberPagination()
        paginator.page_size = 250  # Limit the number of results per page
        result_page = paginator.paginate_queryset(latest_spreads, request)
        
        # Serialize the results
        serializer = latest_SpreadsSerializer(result_page, many=True)
        
        # Return the paginated response
        return paginator.get_paginated_response(serializer.data)


# LATEST MONEYLINE NEEDED


#### Registration

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created successfully!')
            return redirect('login')  # Redirect to the login page after registration
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

@csrf_exempt
def create_checkout_session(request):
    if request.method == 'POST':
        YOUR_DOMAIN = os.getenv('STRIPE_DOMAIN')

        try:
            # Log incoming request body
            logger.info(f"Request body: {request.body.decode('utf-8')}")

            # Use the recurring price ID from the Stripe dashboard
            price_id = 'price_1QmjCGB70pdVZrmYviRQc2Mn'  # Replace with your actual recurring price ID

            # Create a Stripe Checkout session
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price': price_id,  # Use the recurring price ID here
                        'quantity': 1,
                    },
                ],
                mode='subscription',  # Subscription mode
                success_url=f"{YOUR_DOMAIN}/success/",
                cancel_url=f"{YOUR_DOMAIN}/cancel/",
            )

            logger.info(f"Stripe session created: {session.id}")
            return JsonResponse({'id': session.id})

        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)

    else:
        # If not a POST request, return a Method Not Allowed error
        logger.error("Invalid HTTP method.")
        return JsonResponse({'error': 'Invalid HTTP method'}, status=405)
    

def success(request):
    return render(request, 'success.html')  # Create this template

def cancel(request):
    return render(request, 'cancel.html')  # Create this template

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    if not sig_header:
        logger.error("Missing Stripe signature header")
        return JsonResponse({'message': 'Missing Stripe signature header'}, status=400)

    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        # Verify and construct the event from Stripe
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        logger.info(f"Received event: {event['type']}")

        # Handle successful checkout session completion event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            handle_checkout_session(session)
            logger.info(f"Checkout session completed for {session['customer_email']}")

        # Handle successful payment events (optional, if you still want to track payments)
        elif event['type'] == 'invoice.payment_succeeded':
            session = event['data']['object']
            handle_successful_payment(session)
            logger.info(f"Payment succeeded for {session['customer_email']}")

        # Handle subscription cancellation event
        elif event['type'] == 'customer.subscription.deleted':
            session = event['data']['object']
            handle_subscription_cancellation(session)
            logger.info(f"Subscription cancelled for {session['customer_email']}")

        return HttpResponse(status=200)

    except ValueError as e:
        logger.error(f"Invalid payload: {str(e)}")
        return JsonResponse({'message': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Signature verification error: {str(e)}")
        return JsonResponse({'message': 'Invalid signature'}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JsonResponse({'message': 'Internal server error'}, status=500)


def handle_checkout_session(session):
    """Process the successful checkout session here."""
    try:
        # Get the user by Stripe customer ID
        user = get_user_by_stripe_id(session['customer'])
        if user:
            # Extract the subscription ID from the session object
            subscription_id = session['subscription']

            # Handle subscription creation or update
            subscription, created = UserSubscription.objects.update_or_create(
                user=user,
                defaults={
                    'stripe_subscription_id': subscription_id,
                    'status': 'active',  # Mark as active after successful checkout
                    'expiration_date': timezone.now() + timedelta(days=30),  # Assuming a 30-day subscription
                }
            )
            logger.info(f"Subscription created/updated for {user.username}. Subscription ID: {subscription_id}")
    except Exception as e:
        logger.error(f"Error processing checkout session: {str(e)}")


def handle_successful_payment(session):
    """Handles successful payments (if you still want to handle them)."""
    user = get_user_by_stripe_id(session['customer'])
    if user:
        # Calculate the next payment date
        next_payment_date = timezone.now() + timedelta(days=30)

        # Update the subscription
        subscription, created = UserSubscription.objects.update_or_create(
            user=user,
            defaults={
                'stripe_subscription_id': session['subscription'],
                'status': 'active',
                'expiration_date': next_payment_date,
            }
        )


def handle_subscription_cancellation(session):
    """Handles subscription cancellations."""
    user = get_user_by_stripe_id(session['customer'])
    if user:
        subscription = UserSubscription.objects.filter(user=user).first()
        if subscription:
            subscription.status = 'inactive'
            subscription.cancel_date = timezone.now()  # Mark the cancellation date
            subscription.save()
            logger.info(f"Subscription cancelled for {user.username}")


def get_user_by_stripe_id(stripe_customer_id):
    """Retrieve the user based on their Stripe customer ID."""
    try:
        return User.objects.get(stripe_customer_id=stripe_customer_id)
    except User.DoesNotExist:
        logger.error(f"User with Stripe customer ID {stripe_customer_id} not found")
        return None

@api_view(['POST'])
def register_and_get_jwt(request):
    if request.method == 'POST':
        print("Received POST request for registration.")

        # Get the data from the request
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        print(f"Received data - Username: {username}, Email: {email}")

        # Check if all fields are provided
        if not username or not email or not password:
            print("Missing required fields.")
            return Response({"error": "All fields are required."}, status=400)

        # Check if email is unique
        if User.objects.filter(email=email).exists():
            print(f"Email {email} is already taken.")
            return Response({"error": "Email is already taken."}, status=400)

        # Create the user
        try:
            print("Creating user...")
            user = User.objects.create_user(username=username, email=email, password=password)
            print(f"User created: {user.username}")
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            return Response({"error": "User creation failed."}, status=500)

        # Now, create Stripe customer
        try:
            print(f"Creating Stripe customer for email: {email}")
            stripe_customer = stripe.Customer.create(
                email=email,
                description=f"Customer for {username}",
            )
            print(f"Stripe customer created: {stripe_customer}")
        except Exception as e:
            print(f"Error creating Stripe customer: {str(e)}")
            return Response({"error": "Stripe customer creation failed."}, status=400)

        if not stripe_customer.get("id"):
            print("Stripe customer creation failed. Missing Stripe customer ID.")
            return Response({"error": "Stripe customer creation failed."}, status=400)

        print(f"Stripe customer ID: {stripe_customer['id']}")
        stripe_subscription_id = stripe_customer.get("id")

        # Now create the user subscription record
        try:
            print(f"Creating user subscription for user: {user.username}")
            user_subscription = UserSubscription.objects.create(
                user=user,  # Link the user to the subscription
                stripe_subscription_id=stripe_subscription_id,  # Set the subscription ID
                status='active'
            )
            print(f"User subscription created successfully: {stripe_subscription_id}")
        except Exception as e:
            print(f"Error creating user subscription: {str(e)}")
            return Response({"error": "User subscription creation failed."}, status=500)

        # Create JWT token for the user after subscription is created
        print("Creating JWT token for user.")
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        print("JWT token created successfully.")

        return Response({
            'refresh': str(refresh),
            'access': str(access_token),
        })



#login

@api_view(['POST'])
def login_and_get_jwt(request):
    username = request.data.get('username')
    password = request.data.get('password')

    # Check if both fields are provided
    if not username or not password:
        return Response({"error": "Username and password are required."}, status=400)

    # Authenticate the user
    user = authenticate(username=username, password=password)
    if user is None:
        return Response({"error": "Invalid username or password."}, status=401)

    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    })

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def check_subscription(request):
    try:
        # Make sure the user is authenticated
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=401)

        # Get the user's subscription
        subscription = UserSubscription.objects.get(user=request.user)
        trial_end_date = subscription.trial_start_date + timedelta(days=7)

        # Check if trial expired or subscription is still valid
        if subscription.status == 'inactive' and timezone.now() > trial_end_date:
            return Response({"status": "expired", "message": "Trial expired. Please subscribe."})

        if subscription.status == 'active' and subscription.expiration_date and timezone.now() < subscription.expiration_date:
            return Response({"status": "active", "message": "Subscription is active."})

        return Response({"status": "inactive", "message": "Subscription is inactive."})

    except AuthenticationFailed:
        print("Authentication failed: Token might have expired.")
        raise AuthenticationFailed("Authentication credentials were not provided or token expired.")
    except UserSubscription.DoesNotExist:
        return Response({"error": "No subscription found for the user."}, status=404)