from django.shortcuts import render
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
        game_id = request.query_params.get('game_id')
        sport_type = request.query_params.get('sport_type')
        player_name = request.query_params.get('player_name')
        page_number = request.query_params.get('page', 1)
        cache_key = f'props_data_{game_id}_{sport_type}_{player_name}_page_{page_number}'

        # Check cache first
        data = cache.get(cache_key)
        if not data:
            filters = {}
            if game_id:
                filters['game_id'] = game_id
            if sport_type:
                filters['sport_type'] = sport_type
            if player_name:
                filters['player_name__icontains'] = player_name  # Partial match for player name

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
        # Query the DistinctProps model to get all distinct entries
        distinct_props = DistinctProps.objects.all()
        paginator = PageNumberPagination()
        paginator.page_size = 100  # Adjust the number of results per page
        result_page = paginator.paginate_queryset(distinct_props, request)
        serializer = DistinctPropsSerializer(result_page, many=True)
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
        
        # Filter the latest_moneyline table by game_id
        latest_moneyline = latest_Moneyline.objects.filter(game=game_id)[:10]  # Limit to 10 results

        # Paginate the results
        paginator = PageNumberPagination()
        paginator.page_size = 100
        result_page = paginator.paginate_queryset(latest_moneyline, request)
        
        # Serialize the results
        serializer = latest_MoneylineSerializer(result_page, many=True)

        # Return the paginated response
        return paginator.get_paginated_response(serializer.data)


class latest_OverunderListView(APIView):
    def get(self, request):
        latest_overunders = latest_Overunder.objects.all()
        paginator = PageNumberPagination()
        paginator.page_size = 250  # Limit the number of results per page
        result_page = paginator.paginate_queryset(latest_overunders, request)
        serializer = latest_OverunderSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class latest_PropsListView(APIView):
    def get(self, request):
        latest_props = latest_Props.objects.all()
        paginator = PageNumberPagination()
        paginator.page_size = 100  # Limit the number of results per page
        result_page = paginator.paginate_queryset(latest_props, request)
        serializer = latest_PropsSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

class latest_SpreadsListView(APIView):
    def get(self, request):
        latest_spreads = latest_Spreads.objects.all()
        paginator = PageNumberPagination()
        paginator.page_size = 250  # Limit the number of results per page
        result_page = paginator.paginate_queryset(latest_spreads, request)
        serializer = latest_SpreadsSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

# LATEST MONEYLINE NEEDED