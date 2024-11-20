from rest_framework import serializers
from .models import Moneyline, Overunder, Props, Scores, Spreads, UpcomingGames

class MoneylineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moneyline
        fields = '__all__'

class OverunderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Overunder
        fields = '__all__'

class PropsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Props
        fields = '__all__'

class ScoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scores
        fields = '__all__'

class SpreadsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Spreads
        fields = '__all__'

class UpcomingGamesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UpcomingGames
        fields = '__all__'
