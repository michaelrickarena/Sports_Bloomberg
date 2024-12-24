from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Moneyline, Overunder, Props, Scores, Spreads, UpcomingGames
from .serializers import (
    MoneylineSerializer,
    OverunderSerializer,
    PropsSerializer,
    ScoresSerializer,
    SpreadsSerializer,
    UpcomingGamesSerializer,
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


# New View for Chart Data
class MoneylineChartDataView(APIView):
    def get(self, request, game_id):
        try:
            data = get_chart_data(game_id)  # Call the caching function
            return Response(data, status=status.HTTP_200_OK)
        except Moneyline.DoesNotExist:
            return Response(
                {"error": "Game data not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class OverunderListView(APIView):
    def get(self, request):
        overunders = Overunder.objects.all()
        paginator = PageNumberPagination()
        paginator.page_size = 250  # Limit the number of results per page
        result_page = paginator.paginate_queryset(overunders, request)
        serializer = OverunderSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class PropsListView(APIView):
    def get(self, request):
        props = Props.objects.all()
        paginator = PageNumberPagination()
        paginator.page_size = 250  # Limit the number of results per page
        result_page = paginator.paginate_queryset(props, request)
        serializer = PropsSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class ScoresListView(APIView):
    def get(self, request):
        scores = Scores.objects.all()
        paginator = PageNumberPagination()
        paginator.page_size = 250  # Limit the number of results per page
        result_page = paginator.paginate_queryset(scores, request)
        serializer = ScoresSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class SpreadsListView(APIView):
    def get(self, request):
        spreads = Spreads.objects.all()
        paginator = PageNumberPagination()
        paginator.page_size = 250  # Limit the number of results per page
        result_page = paginator.paginate_queryset(spreads, request)
        serializer = SpreadsSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class UpcomingGamesListView(APIView):
    def get(self, request):
        # Define the cache key
        cache_key = "upcoming_games_all"

        # Check if data is available in the cache
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info("Cache hit for upcoming games.")
            return Response(cached_data)  # Return cached response

        # If not in cache, fetch all data from the database
        logger.info("Cache miss for upcoming games. Fetching from database.")
        
        # Fetch all rows from the UpcomingGames table
        upcoming_games = UpcomingGames.objects.all()

        # Serialize the data
        serializer = UpcomingGamesSerializer(upcoming_games, many=True)

        # Cache the result for 2 hours (7200 seconds)
        cache.set(cache_key, serializer.data, timeout=7200)
        logger.info("Upcoming games data cached.")

        return Response(serializer.data)
