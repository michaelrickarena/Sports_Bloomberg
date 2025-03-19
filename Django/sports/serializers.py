from rest_framework import serializers
from .models import Moneyline, Overunder, Props, Scores, Spreads, UpcomingGames, latest_Moneyline, latest_Overunder, latest_Props, latest_Spreads, DistinctProps, UserBet, ExpectedValueMoneyline, ExpectedValueProps


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
    game_id = serializers.SlugRelatedField(
        slug_field='game_id',
        queryset=Scores.objects.all(),
        source='game'
    )

    class Meta:
        model = UserBet
        fields = [
            'id', 'user', 'game_id', 'bookie', 'bet_type', 'line',
            'alert_threshold', 'is_active', 'team_bet_on', 'created_at',
            'bet_amount'
        ]
        read_only_fields = ['user', 'created_at']

    def to_representation(self, instance):
        # Get the default serialized data
        data = super().to_representation(instance)
        # Convert id and user to strings
        data['id'] = str(data['id'])
        data['user'] = str(data['user'])
        return data

    def validate_odds(self, value):
        if value == 0:
            raise serializers.ValidationError("Odds cannot be zero.")
        if not isinstance(value, int):
            raise serializers.ValidationError("Odds must be an integer (no decimal or float values allowed).")
        return value

class ExpectedValueMoneylineSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpectedValueMoneyline
        fields = '__all__'


class ExpectedValuePropsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpectedValueProps
        fields = '__all__'