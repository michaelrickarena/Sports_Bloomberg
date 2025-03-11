from rest_framework import serializers
from .models import Moneyline, Overunder, Props, Scores, Spreads, UpcomingGames, latest_Moneyline, latest_Overunder, latest_Props, latest_Spreads, DistinctProps, UserBet


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

class latest_MoneylineSerializer(serializers.ModelSerializer):
    class Meta:
        model = latest_Moneyline
        fields = '__all__'

class latest_OverunderSerializer(serializers.ModelSerializer):
    class Meta:
        model = latest_Overunder
        fields = '__all__'

class latest_PropsSerializer(serializers.ModelSerializer):
    class Meta:
        model = latest_Props
        fields = '__all__'

class latest_SpreadsSerializer(serializers.ModelSerializer):
    class Meta:
        model = latest_Spreads
        fields = '__all__'

class DistinctPropsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistinctProps
        fields = '__all__'  

class UserBetSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBet
        fields = "__all__"
        read_only_fields = ["user", "created_at"]

    def validate_odds(self, value):
        if value == 0:
            raise serializers.ValidationError("Odds cannot be zero.")
        # Ensure the odds are integers (no decimals or floats allowed)
        if not isinstance(value, int):
            raise serializers.ValidationError("Odds must be an integer (no decimal or float values allowed).")
        return value