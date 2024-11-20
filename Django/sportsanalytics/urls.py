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
from sports.views import MoneylineListView, OverunderListView, PropsListView, ScoresListView, SpreadsListView, UpcomingGamesListView
from django.http import HttpResponse

# Define the homepage view
def homepage(request):
    return HttpResponse("Welcome to the Sports Analytics API!")

urlpatterns = [
    path('', homepage, name='home'),  # This adds a view for the root path
    path('admin/', admin.site.urls),
    path('api/moneyline/', MoneylineListView.as_view(), name='moneyline_list'),
    path('api/overunder/', OverunderListView.as_view(), name='overunder_list'),
    path('api/props/', PropsListView.as_view(), name='props_list'),
    path('api/scores/', ScoresListView.as_view(), name='scores_list'),
    path('api/spreads/', SpreadsListView.as_view(), name='spreads_list'),
    path('api/upcoming_games/', UpcomingGamesListView.as_view(), name='upcoming_games_list'),
]
