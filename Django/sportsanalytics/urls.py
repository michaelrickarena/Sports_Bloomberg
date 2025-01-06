"""
URL configuration for sportsanalytics project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from sports.views import (
    MoneylineListView, MoneylineChartDataView, OverunderListView, PropsListView, ScoresListView, 
    SpreadsListView, UpcomingGamesListView, OverunderChartDataView, PropsChartDataView, SpreadsChartDataView, 
    latest_MoneylineListView, latest_OverunderListView, latest_PropsListView, latest_SpreadsListView, DistinctPropsListView
)
from django.http import HttpResponse

# Define the homepage view
def homepage(request):
    return HttpResponse("Welcome to the Sports Analytics API!")

urlpatterns = [
    path('', homepage, name='home'),  # Root path for the homepage
    path('admin/', admin.site.urls),

    # List Views
    path("api/moneyline/", MoneylineListView.as_view(), name="moneyline-list"),
    path('api/overunder/', OverunderListView.as_view(), name='overunder_list'),
    path('api/props/', PropsListView.as_view(), name='props_list'),
    path('api/scores/', ScoresListView.as_view(), name='scores_list'),
    path('api/spreads/', SpreadsListView.as_view(), name='spreads_list'),
    path('api/upcoming_games/', UpcomingGamesListView.as_view(), name='upcoming_games_list'),
    path('api/distinct_props/', DistinctPropsListView.as_view(), name='distinct_props_list'),

    # Chart Data Views
    path("api/moneyline/chart/", MoneylineChartDataView.as_view(), name="moneyline-chart-data"),
    path("api/overunder/chart/", OverunderChartDataView.as_view(), name="overunder-chart-data"),
    path("api/props/chart/", PropsChartDataView.as_view(), name="props-chart-data"),
    path("api/spreads/chart/", SpreadsChartDataView.as_view(), name="spreads-chart-data"),

    # Additional Paths for latest data (if needed)
    path('api/latest_moneyline/', latest_MoneylineListView.as_view(), name='latest_moneyline_list'),
    path('api/latest_overunder/', latest_OverunderListView.as_view(), name='latest_overunder_list'),
    path('api/latest_props/', latest_PropsListView.as_view(), name='latest_props_list'),
    path('api/latest_spreads/', latest_SpreadsListView.as_view(), name='latest_spreads_list'),
]

