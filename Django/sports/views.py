from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Moneyline, Overunder, Props, Scores, Spreads, UpcomingGames
from .serializers import MoneylineSerializer, OverunderSerializer, PropsSerializer, ScoresSerializer, SpreadsSerializer, UpcomingGamesSerializer
from rest_framework.pagination import PageNumberPagination

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

class MoneylineListView(APIView):
    def get(self, request):
        moneylines = Moneyline.objects.all()
        paginator = PageNumberPagination()
        paginator.page_size = 10  # Limit the number of results per page
        result_page = paginator.paginate_queryset(moneylines, request)
        serializer = MoneylineSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class OverunderListView(APIView):
    def get(self, request):
        overunders = Overunder.objects.all()
        paginator = PageNumberPagination()
        paginator.page_size = 10  # Limit the number of results per page
        result_page = paginator.paginate_queryset(overunders, request)
        serializer = OverunderSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class PropsListView(APIView):
    def get(self, request):
        props = Props.objects.all()
        paginator = PageNumberPagination()
        paginator.page_size = 10  # Limit the number of results per page
        result_page = paginator.paginate_queryset(props, request)
        serializer = PropsSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class ScoresListView(APIView):
    def get(self, request):
        scores = Scores.objects.all()
        paginator = PageNumberPagination()
        paginator.page_size = 10  # Limit the number of results per page
        result_page = paginator.paginate_queryset(scores, request)
        serializer = ScoresSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class SpreadsListView(APIView):
    def get(self, request):
        spreads = Spreads.objects.all()
        paginator = PageNumberPagination()
        paginator.page_size = 10  # Limit the number of results per page
        result_page = paginator.paginate_queryset(spreads, request)
        serializer = SpreadsSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class UpcomingGamesListView(APIView):
    def get(self, request):
        upcoming_games = UpcomingGames.objects.all()
        paginator = PageNumberPagination()
        paginator.page_size = 10  # Limit the number of results per page
        result_page = paginator.paginate_queryset(upcoming_games, request)
        serializer = UpcomingGamesSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
