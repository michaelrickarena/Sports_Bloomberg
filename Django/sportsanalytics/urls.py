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
from django.urls import path, include
from sports.views import (
    MoneylineListView, MoneylineChartDataView, OverunderListView, PropsListView, ScoresListView, 
    SpreadsListView, UpcomingGamesListView, OverunderChartDataView, PropsChartDataView, SpreadsChartDataView, 
    latest_MoneylineListView, latest_OverunderListView, latest_PropsListView, latest_SpreadsListView, DistinctPropsListView, 
    create_checkout_session, cancel, success, stripe_webhook, login_and_get_jwt, cancel_subscription
)
from django.http import HttpResponse
from sports import views
from django.contrib.auth import views as auth_views
from sports.views import register_and_get_jwt
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


# Define the homepage view
def homepage(request):
    return HttpResponse("Welcome to the Sports Analytics API!")

urlpatterns = [
    path('', homepage, name='home'),  # Root path for the homepage
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', views.register, name='register'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('api/create-checkout-session/', create_checkout_session, name='create-checkout-session'),
    path('success/', views.success, name='success'),
    path('cancel/', views.cancel, name='cancel'),  # Cancel page route
    path('webhook/', stripe_webhook, name='stripe-webhook'),
    path('api/check-subscription', views.check_subscription, name='check_subscription'),

    #jwt
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/login/', login_and_get_jwt, name='login_and_get_jwt'),
    path('api/register_and_get_jwt/', register_and_get_jwt, name='register_and_get_jwt'),
    path("api/cancel-subscription/", cancel_subscription, name="cancel-subscription"),


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

