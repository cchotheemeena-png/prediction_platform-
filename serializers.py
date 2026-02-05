from rest_framework import serializers
from .models import Bet, GameRound

class BetSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = Bet
        fields = '__all__'

class GameRoundSerializer(serializers.ModelSerializer):
    seconds_remaining = serializers.ReadOnlyField()
    total_bets = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = GameRound
        fields = '__all__'
    
    def get_total_bets(self, obj):
        return obj.bets.count()
    
    def get_total_amount(self, obj):
        return obj.bets.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
