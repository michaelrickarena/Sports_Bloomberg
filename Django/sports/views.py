from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Moneyline, Overunder, Props, Scores, Spreads, UpcomingGames, latest_Moneyline, latest_Overunder, latest_Props, latest_Spreads, DistinctProps, ExpectedValueMoneyline, ExpectedValueProps, UserBet, Arbitrage
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
    DistinctPropsSerializer, 
    ExpectedValueMoneylineSerializer, 
    ExpectedValuePropsSerializer,
    UserBetSerializer,
    ArbitrageSerializer
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
from django.contrib.auth import get_user_model
import jwt
from django.contrib.auth import login  # Import login function
from sports.users.utils import generate_email_verification_token
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework import generics, permissions
import boto3
import time
import datetime

load_dotenv()

STRIPE_DOMAIN = os.getenv('STRIPE_DOMAIN')
FRONT_END_DOMAIN = os.getenv('FRONT_END_DOMAIN')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')

logger = logging.getLogger("logsport")

class MoneylineListView(APIView):
    def get(self, request):
        print(f"MoneylineListView START: {datetime.datetime.utcnow().isoformat()}Z")
        game_id = request.query_params.get('game_id')
        page_number = request.query_params.get('page', 1)
        cache_key = f'moneyline_data_{game_id}_page_{page_number}'

        # Check cache first
        data = cache.get(cache_key)
        if not data:
            t0 = time.time()
            if game_id:
                # Only fetch needed fields to reduce memory usage
                moneylines = Moneyline.objects.filter(game_id=game_id).only(
                    "id", "game_id", "bookie", "matchup_type", "home_team", "line_1", "away_team", "line_2", "event_timestamp", "last_updated_timestamp", "sport_type"
                ).order_by('last_updated_timestamp')
            else:
                moneylines = Moneyline.objects.all().only(
                    "id", "game_id", "bookie", "matchup_type", "home_team", "line_1", "away_team", "line_2", "event_timestamp", "last_updated_timestamp", "sport_type"
                ).order_by('last_updated_timestamp')

            t1 = time.time()
            paginator = PageNumberPagination()
            paginator.page_size = 250
            result_page = paginator.paginate_queryset(moneylines, request)
            t2 = time.time()
            serializer = MoneylineSerializer(result_page, many=True)
            t3 = time.time()
            data = paginator.get_paginated_response(serializer.data).data
            cache.set(cache_key, data, timeout=7200)

            # Timing logs for debugging
            print(f"Query: {t1-t0:.2f}s, Pagination: {t2-t1:.2f}s, Serialization: {t3-t2:.2f}s, Total: {t3-t0:.2f}s")

        return Response(data)

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
        prop_type   = request.query_params.get('prop_type')
        page_number = request.query_params.get('page', 1)
        cache_key   = f'athena_props_{player_name}_{prop_type}_page_{page_number}'

        # Attempt to fetch from cache
        cached = cache.get(cache_key)
        if cached is not None:
            # For paginated case, must be dict
            if player_name and prop_type:
                if isinstance(cached, dict):
                    return Response(cached)
                else:
                    cache.delete(cache_key)
            else:
                # For other cases, must be list
                if isinstance(cached, list):
                    return Response(cached)
                else:
                    cache.delete(cache_key)

        try:
            # Build WHERE clause
            wheres = []
            if player_name:
                wheres.append(f"player_name LIKE '%{player_name}%'" )
            if prop_type:
                wheres.append(f"prop_type = '{prop_type}'")
            where_sql = " AND ".join(wheres) if wheres else "1=1"

            # Execute Athena query
            athena = boto3.client('athena', region_name=settings.AWS_DEFAULT_REGION)
            query = f"""
                SELECT * FROM props
                WHERE {where_sql}
                ORDER BY last_updated_timestamp
            """
            resp = athena.start_query_execution(
                QueryString=query,
                QueryExecutionContext={'Database': 'default'},
                ResultConfiguration={'OutputLocation': 's3://sports-data-csv/athena-query-results/'}
            )
            qid = resp['QueryExecutionId']
            state = 'RUNNING'
            while state in ('RUNNING', 'QUEUED'):
                time.sleep(1)
                status = athena.get_query_execution(QueryExecutionId=qid)['QueryExecution']['Status']
                state = status['State']
            if state != 'SUCCEEDED':
                reason = status.get('StateChangeReason')
                return Response({'error': 'Athena query failed', 'state': state, 'reason': reason}, status=500)

            # Process results
            result = athena.get_query_results(QueryExecutionId=qid)
            cols = [c['Name'] for c in result['ResultSet']['ResultSetMetadata']['ColumnInfo']]
            rows = []
            for r in result['ResultSet']['Rows'][1:]:
                vals = [d.get('VarCharValue') for d in r['Data']]
                item = dict(zip(cols, vals))
                # Rename & cast
                if 'game_id' in item:
                    item['game'] = item.pop('game_id')
                if 'betting_line' in item and item['betting_line'] is not None:
                    try:
                        item['betting_line'] = int(float(item['betting_line']))
                    except (ValueError, TypeError):
                        item['betting_line'] = None
                rows.append(item)

            # Branch on pagination criteria
            if player_name and prop_type:
                # Paginate rows
                paginator = PageNumberPagination()
                paginator.page_size = 250
                page = paginator.paginate_queryset(rows, request)
                response = paginator.get_paginated_response(page)
                cache.set(cache_key, response.data, timeout=7200)
                return response
            else:
                # Return raw list
                cache.set(cache_key, rows, timeout=7200)
                return Response(rows)

        except Exception as e:
            import traceback; traceback.print_exc()
            return Response({'error': str(e)}, status=500)


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
        player_name = request.query_params.get('player_name')
        prop_type = request.query_params.get('prop_type')
        page_number = request.query_params.get('page', 1)

        # Determine mode and cache key
        is_unique_prop_types = bool(player_name and not prop_type)
        cache_key = (
            f'athena_unique_prop_types_{player_name}_page_{page_number}'
            if is_unique_prop_types
            else f'athena_props_{player_name}_{prop_type}_page_{page_number}'
        )

        # Retrieve from cache
        cached = cache.get(cache_key)
        # For specific prop_type, only accept list cache, not paginated dict
        if prop_type and player_name:
            if isinstance(cached, list):
                return Response(cached)
        else:
            if cached:
                return Response(cached)

        try:
            # Build Athena query
            if is_unique_prop_types:
                query = f"""
                    SELECT DISTINCT prop_type FROM latest_props
                    WHERE player_name LIKE '%{player_name}%'
                    ORDER BY prop_type
                """
            else:
                wheres = []
                if player_name:
                    wheres.append(f"player_name LIKE '%{player_name}%'" )
                if prop_type:
                    wheres.append(f"prop_type = '{prop_type}'")
                where_sql = " AND ".join(wheres) if wheres else "1=1"
                query = f"""
                    SELECT * FROM latest_props
                    WHERE {where_sql}
                    ORDER BY last_updated_timestamp
                """

            # Execute Athena query
            athena = boto3.client('athena', region_name=settings.AWS_DEFAULT_REGION)
            resp = athena.start_query_execution(
                QueryString=query,
                QueryExecutionContext={'Database': 'default'},
                ResultConfiguration={'OutputLocation': 's3://sports-data-csv/athena-query-results/'}
            )
            qid = resp['QueryExecutionId']
            state = 'RUNNING'
            while state in ('RUNNING', 'QUEUED'):
                time.sleep(1)
                status = athena.get_query_execution(QueryExecutionId=qid)['QueryExecution']['Status']
                state = status['State']
            if state != 'SUCCEEDED':
                reason = status.get('StateChangeReason')
                return Response({'error': 'Athena query failed', 'state': state, 'reason': reason}, status=500)

            # Fetch and process results
            res = athena.get_query_results(QueryExecutionId=qid)
            cols = [c['Name'] for c in res['ResultSet']['ResultSetMetadata']['ColumnInfo']]
            rows = []
            for r in res['ResultSet']['Rows'][1:]:
                vals = [d.get('VarCharValue') for d in r['Data']]
                record = dict(zip(cols, vals))
                # Rename and cast
                if 'game_id' in record:
                    record['game'] = record.pop('game_id')
                if record.get('betting_line') is not None:
                    try:
                        record['betting_line'] = int(float(record['betting_line']))
                    except (ValueError, TypeError):
                        record['betting_line'] = None
                rows.append(record)

            # Specific prop_type: return raw list and cache
            if prop_type and player_name:
                cache.set(cache_key, rows, timeout=7200)
                return Response(rows)

            # Unique prop types: paginate list of prop_type strings
            items = [r['prop_type'] for r in rows]
            paginator = PageNumberPagination()
            paginator.page_size = 250
            page = paginator.paginate_queryset(items, request)
            paginated_response = paginator.get_paginated_response(page)
            cache.set(cache_key, paginated_response.data, timeout=7200)
            return paginated_response

        except Exception as e:
            import traceback; traceback.print_exc()
            return Response({'error': str(e)}, status=500)


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


stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

@csrf_exempt
def create_checkout_session(request):
    if request.method == 'POST':
        # Log the Authorization header to see the token being passed
        auth_header = request.headers.get('Authorization')
        if auth_header:
            logger.info(f"Authorization header: {auth_header}")
        else:
            logger.warning("No Authorization header found")
        
        # Ensure token is passed in the Authorization header
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Token is missing or invalid'}, status=401)

        token = auth_header.split(' ')[1]  # Get the token part after 'Bearer'

        try:
            # Decode the JWT token using the secret key in settings
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

            # Retrieve the user associated with the token
            user_id = payload.get('user_id')
            logger.info(f"user_id: {user_id}")
            if not user_id:
                return JsonResponse({'error': 'User ID not found in token'}, status=401)
            
            try:
                user = get_user_model().objects.get(id=user_id)
                logger.info(f"database pull for user_id: {user_id}")
            except get_user_model().DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=401)

            # Authenticate the user manually
            request.user = user
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token has expired'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Invalid token'}, status=401)

        YOUR_DOMAIN = os.getenv('STRIPE_DOMAIN')

        try:
            # Log incoming request body
            logger.info(f"Request body: {request.body.decode('utf-8')}")

            # Retrieve the Stripe customer ID from the user's subscription
            try:
                stripe_customer_id = request.user.usersubscription.stripe_customer_id
                logger.info(f"STRIPE CUSTOMER ID -------- {stripe_customer_id}")
            except AttributeError:
                return JsonResponse({'error': 'Stripe customer ID not found for this user'}, status=400)

            # Use the recurring price ID from the Stripe dashboard
            price_id = 'price_1QmicdB70pdVZrmYn8ILuDSY'  # Replace with your actual recurring price ID

            # Create a Stripe Checkout session
            session = stripe.checkout.Session.create(
                customer=stripe_customer_id,  # Link to the user's Stripe customer ID
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,  # Use the recurring price ID here
                    'quantity': 1,
                }],
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
            logger.info(f"Checkout session completed for {session.get('customer_email', 'unknown email')}")

        # Handle successful payment events (if you still want to track payments)
        elif event['type'] == 'invoice.payment_succeeded':
            session = event['data']['object']
            handle_successful_payment(session)
            logger.info(f"Payment succeeded for {session.get('customer_email', 'unknown email')}")

        # Handle subscription cancellation event
        elif event['type'] == 'customer.subscription.deleted':
            session = event['data']['object']
            handle_subscription_cancellation(session)
            logger.info(f"Subscription cancelled for {session.get('customer_email', 'unknown email')}")

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
    """Process the successful checkout session."""
    try:
        # Retrieve the user via the Stripe customer ID
        user = get_user_by_stripe_id(session['customer'])
        if user:
            subscription_id = session.get('subscription')
            # Create or update the subscription, and store the Stripe customer ID
            subscription, created = UserSubscription.objects.update_or_create(
                user=user,
                defaults={
                    'stripe_subscription_id': subscription_id,
                    'stripe_customer_id': session['customer'],  # Set the Stripe customer ID
                    'status': 'active',
                    'expiration_date': timezone.now() + timedelta(days=30),  # For example, a 30-day subscription
                }
            )
            logger.info(f"Subscription created/updated for {user.username}. Subscription ID: {subscription_id}")
    except Exception as e:
        logger.error(f"Error processing checkout session: {str(e)}")


def handle_successful_payment(session):
    """Handles successful payment events."""
    try:
        user = get_user_by_stripe_id(session['customer'])
        if user:
            next_payment_date = timezone.now() + timedelta(days=30)
            subscription, created = UserSubscription.objects.update_or_create(
                user=user,
                defaults={
                    'stripe_subscription_id': session.get('subscription'),
                    'stripe_customer_id': session['customer'],
                    'status': 'active',
                    'expiration_date': next_payment_date,
                }
            )
            logger.info(f"Successful payment processed for {user.username}")
    except Exception as e:
        logger.error(f"Error processing successful payment: {str(e)}")


def handle_subscription_cancellation(session):
    """Handles subscription cancellation events."""
    try:
        user = get_user_by_stripe_id(session['customer'])
        if user:
            subscription = UserSubscription.objects.filter(user=user).first()
            if subscription:
                subscription.status = 'inactive'
                subscription.cancel_date = timezone.now()
                subscription.save()
                logger.info(f"Subscription cancelled for {user.username}")
    except Exception as e:
        logger.error(f"Error processing subscription cancellation: {str(e)}")


def get_user_by_stripe_id(stripe_customer_id):
    """
    Retrieve the user associated with a given Stripe customer ID
    from the UserSubscription model.
    """
    try:
        subscription = UserSubscription.objects.get(stripe_customer_id=stripe_customer_id)
        return subscription.user
    except UserSubscription.DoesNotExist:
        logger.error(f"User with Stripe customer ID {stripe_customer_id} not found")
        return None


def send_verification_email(request, user, uid, token):
    # Point to your front-end verification URL
    verification_url = f"{FRONT_END_DOMAIN}/verify-email?uid={uid}&token={token}"
    
    subject = "Verify Your Email - SmartLines"
    message = (
        f"Welcome to SmartLines, {user.username}!\n\n"
        "Thank you for signing up — you're just one step away from unlocking the best betting insights.\n\n"
        "Click the link below to verify your email and activate your account:\n\n"
        f"{verification_url}\n\n"
        "If you have any questions, feel free to reply to this email — we're happy to help.\n\n"
        "The SmartLines Team"
    )
    
    send_mail(
        subject, 
        message, 
        f"SmartLines <{EMAIL_HOST_USER}>",  # More branded sender
        [user.email]
    )



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

        # Create or get the user
        try:
            print("Creating user...")
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': email, 'password': password}
            )
            if created:
                user.set_password(password)  # Set password for new user
                user.is_active = False  # Set the user as inactive until email verification
                user.save()
                print(f"User created: {user.username}")
            else:
                print(f"User {username} already exists, proceeding...")
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            return Response({"error": "User creation failed."}, status=500)

        # Create Stripe customer (optional)
        try:
            print(f"Creating Stripe customer for email: {email}")
            stripe_customer = stripe.Customer.create(
                email=email,
                description=f"Customer for {username}",
            )
            print(f"Stripe customer created: {stripe_customer}")
            stripe_customer_id = stripe_customer.get("id")
            if not stripe_customer_id:
                print("Stripe customer creation failed. Missing Stripe customer ID.")
                return Response({"error": "Stripe customer creation failed."}, status=400)
            print(f"Stripe customer ID: {stripe_customer_id}")
        except Exception as e:
            print(f"Error creating Stripe customer: {str(e)}")
            return Response({"error": "Stripe customer creation failed."}, status=400)

        # Create or update user subscription
        try:
            print(f"Creating/updating user subscription for user: {user.username}")
            subscription, sub_created = UserSubscription.objects.get_or_create(
                user=user,
                defaults={
                    'stripe_customer_id': stripe_customer_id,
                    'status': 'active'
                }
            )
            if not sub_created:
                print(f"Subscription exists for {user.username}, updating Stripe ID")
                subscription.stripe_customer_id = stripe_customer_id
                subscription.status = 'active'
                subscription.save()
            print(f"User subscription handled successfully: {subscription.stripe_customer_id}")
        except Exception as e:
            print(f"Error handling user subscription: {str(e)}")
            return Response({"error": "User subscription creation failed."}, status=500)

        # Generate email verification token and send email
        uid, token = generate_email_verification_token(user)
        send_verification_email(request, user, uid, token)

        # Create JWT token (but don't log them in yet)
        print("JWT token creation skipped for inactive user.")
        
        return Response({
            'message': 'Please check your email to verify your account.',
        })
    

@api_view(['POST'])
def login_and_get_jwt(request):
    login_identifier = request.data.get('username')  # Could be either username or email
    password = request.data.get('password')

    if not login_identifier or not password:
        return Response({"error": "Username or email and password are required."}, status=400)

    # Try to identify whether it's a username or email
    if '@' in login_identifier:  # This is likely an email address
        try:
            user = User.objects.get(email=login_identifier)
        except User.DoesNotExist:
            return Response({"error": "Invalid username or email or password."}, status=401)
    else:
        user = authenticate(username=login_identifier, password=password)
        if user is None:
            return Response({"error": "Invalid username or password."}, status=401)

    # If authentication fails
    if not user.check_password(password):
        return Response({"error": "Invalid username or email or password."}, status=401)

    if not user.is_active:
        return Response({"error": "Account is not active. Please verify your email."}, status=400)

    login(request, user)

    # Check subscription status
    subscription_status = "inactive"  # Default status if no subscription found

    subscription = UserSubscription.objects.filter(user=user).first()
    if subscription:
        logger.info(f"Subscription found for {user.username}, expiration date: {subscription.expiration_date}")

        if subscription.expiration_date and subscription.expiration_date >= timezone.now():
            subscription_status = subscription.status
        else:
            subscription.status = 'inactive'
            subscription.save()
            logger.info(f"Subscription expired for {user.username}. Status set to inactive.")
            subscription_status = 'inactive'
    else:
        logger.info(f"No subscription found for {user.username}")

    refresh = RefreshToken.for_user(user)

    response = JsonResponse({
        'message': 'Login successful',
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'subscription_active': subscription_status,  # Pass the exact subscription status
    })

    response.set_cookie("refresh_token", str(refresh), httponly=True, secure=True, samesite="None", max_age=86400)
    response.set_cookie("access_token", str(refresh.access_token), httponly=True, secure=True, samesite="None", max_age=86400)

    return response




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

        if subscription.status == 'active' or subscription.status == 'cancelling' and subscription.expiration_date and timezone.now() < subscription.expiration_date:
            return Response({"status": "active", "message": "Subscription is active."})

        return Response({"status": "inactive", "message": "Subscription is inactive."})

    except AuthenticationFailed:
        print("Authentication failed: Token might have expired.")
        raise AuthenticationFailed("Authentication credentials were not provided or token expired.")
    except UserSubscription.DoesNotExist:
        return Response({"error": "No subscription found for the user."}, status=404)
    


@api_view(['POST'])
@authentication_classes([JWTAuthentication])  # Uses JWT for authentication
@permission_classes([IsAuthenticated])  # Ensures user is logged in
def cancel_subscription(request):
    """Cancels the user's active subscription."""
    try:
        # Get the user's subscription
        subscription = UserSubscription.objects.filter(user=request.user, status="active").first()

        if not subscription:
            return JsonResponse({"error": "No active subscription found."}, status=400)

        # Cancel the Stripe subscription
        stripe.Subscription.modify(subscription.stripe_subscription_id, cancel_at_period_end=True)

        # Update the subscription status in the database
        subscription.status = "cancelling"  # Indicate that it's scheduled to cancel
        subscription.save()

        logger.info(f"User {request.user.username} scheduled subscription cancellation.")

        return JsonResponse({"message": "Subscription cancellation scheduled."})
    
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error during cancellation: {str(e)}")
        return JsonResponse({"error": "Failed to cancel subscription. Try again."}, status=500)
    
    except Exception as e:
        logger.error(f"Error cancelling subscription: {str(e)}")
        return JsonResponse({"error": "You currently do not have a subscription."}, status=500)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_subscription_details(request):
    """Returns the user's subscription details, including expiration date."""
    try:
        # Fetch the most recent subscription (active or expired)
        subscription = UserSubscription.objects.filter(user=request.user).order_by('-expiration_date').first()

        if not subscription:
            return JsonResponse({"message": "No subscription found.", "expiration_date": None})

        return JsonResponse({
            "message": "Subscription details retrieved.",
            "expiration_date": subscription.expiration_date.strftime("%Y-%m-%d") if subscription.expiration_date else None
        })

    except Exception as e:
        logger.error(f"Error fetching subscription details: {str(e)}")
        return JsonResponse({"error": "An unexpected error occurred."}, status=500)



@api_view(['POST'])
def verify_email(request):
    # Debugging: Log the raw request body
    print(f"Raw request body: {request.body}")

    # Parse JSON data from request
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return Response({"error": "Invalid JSON in request body."}, status=400)

    # Extract uid and token from request data
    uid = data.get('uid')
    token = data.get('token')

    # Debugging: Log the extracted uid and token
    print(f"Extracted UID: {uid}, Extracted Token: {token}")

    if not uid or not token:
        return Response({"error": "Invalid verification link."}, status=400)

    try:
        # Decode the UID and fetch the user
        uid = urlsafe_base64_decode(uid).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({"error": "Invalid verification link."}, status=400)

    # Validate the token
    if default_token_generator.check_token(user, token):
        user.is_active = True  # Activate the user
        user.save()
        return Response({"message": "Email verified successfully."})
    else:
        return Response({"error": "Invalid token."}, status=400)
    
@api_view(['POST'])
def password_reset_request(request):
    email = request.data.get('email')

    if not email:
        return JsonResponse({"detail": "Email is required."}, status=400)

    try:
        user = get_user_model().objects.get(email=email)
    except get_user_model().DoesNotExist:
        return JsonResponse({"detail": "Email not found."}, status=404)

    # Generate password reset token
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(str(user.pk).encode())

    # Update reset link to point to frontend (replace with actual frontend URL)

    reset_link = f"{FRONT_END_DOMAIN}/password-reset-confirm/{uid}/{token}/"

    # Send the password reset email
    subject = "Password Reset Request"
    message = f"Click the link below to reset your password:\n\n{reset_link}\n\nIf you didn't request this, please ignore this email."

    send_mail(subject, message, 'noreply@yourdomain.com', [email])

    return JsonResponse({"detail": "Password reset email sent."}, status=200)



@api_view(['POST'])
def password_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, get_user_model().DoesNotExist):
        return JsonResponse({"detail": "Invalid token or user."}, status=400)

    if not default_token_generator.check_token(user, token):
        return JsonResponse({"detail": "Invalid or expired token."}, status=400)

    password = request.data.get('password')
    if not password:
        return JsonResponse({"detail": "Password is required."}, status=400)

    user.set_password(password)
    user.save()

    return JsonResponse({"detail": "Password has been reset successfully."}, status=200)



class UserBetCreateView(APIView):
    queryset = UserBet.objects.all()
    serializer_class = UserBetSerializer
    permission_classes = [IsAuthenticated]  # Ensures the user is authenticated

    def post(self, request, *args, **kwargs):
        # Check the Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            logger.error("Authorization header missing")
            return Response({"detail": "Authorization header missing"}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            # Extract token from Authorization header
            token = auth_header.split(' ')[1]
            # This will trigger the validation of the token and associate the user with the request
            user, _ = JWTAuthentication().authenticate(request)
        except Exception as e:
            return Response({"detail": "Invalid or expired token"}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = UserBetSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            serializer.save()
            logger.debug("Bet successfully created.")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Validation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserBetListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Get all bets for the authenticated user
        user_bets = UserBet.objects.filter(user=request.user)
        serializer = UserBetSerializer(user_bets, many=True)
        
        # Debugging: Print retrieved data in the console
        print("User Bets Data:", serializer.data)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserBetDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
        try:
            bet = UserBet.objects.get(pk=pk, user=request.user)
            bet.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except UserBet.DoesNotExist:
            return Response({"detail": "Bet not found"}, status=status.HTTP_404_NOT_FOUND)
        

class ExpectedValueMoneylineListView(generics.ListAPIView):
    queryset = ExpectedValueMoneyline.objects.all()
    serializer_class = ExpectedValueMoneylineSerializer


class ExpectedValuePropsListView(generics.ListAPIView):
    queryset = ExpectedValueProps.objects.all()
    serializer_class = ExpectedValuePropsSerializer


class ArbitrageListView(generics.ListAPIView):
    queryset = Arbitrage.objects.all()
    serializer_class = ArbitrageSerializer