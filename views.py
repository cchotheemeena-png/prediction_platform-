from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from core.permissions import IsAdminUser
from .models import GameRound, Bet
from .serializers import BetSerializer, GameRoundSerializer
from wallet.models import Wallet, Transaction
from .utils import settle_bets
from decimal import Decimal
import uuid

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_round(request):
    round_obj = GameRound.objects.filter(status__in=['active', 'locked']).first()
    if round_obj:
        serializer = GameRoundSerializer(round_obj)
        return Response(serializer.data)
    return Response({'error': 'No active round'}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_bet(request):
    wallet = request.user.wallet
    amount = Decimal(request.data['amount'])
    
    if wallet.main_balance < amount:
        return Response({'error': 'Insufficient balance'}, status=400)
    
    # Atomic transaction
    with transaction.atomic():
        # Lock funds
        wallet.main_balance -= amount
        wallet.locked_balance += amount
        wallet.save()
        
        bet = Bet.objects.create(
            user=request.user,
            round_id=request.data['round_id'],
            bet_type=request.data['bet_type'],
            selection=request.data['selection'],
            amount=amount,
            payout_multiplier=request.data.get('multiplier', 2.0)
        )
        
        Transaction.objects.create(
            wallet=wallet,
            tx_id=uuid.uuid4(),
            amount=-amount,
            type='bet_placed',
            reference_id=f"bet_{bet.id}"
        )
    
    # WebSocket broadcast
    from channels.layers import get_channel_layer
    channel_layer = get_channel_layer()
    # Implementation for broadcast
    
    return Response(BetSerializer(bet).data)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def declare_result(request, round_id):
    round_obj = GameRound.objects.get(id=round_id, status='locked')
    
    round_obj.result_color = request.data['color']
    round_obj.result_number = int(request.data['number'])
    round_obj.result_size = 'big' if round_obj.result_number >= 5 else 'small'
    round_obj.status = 'settled'
    round_obj.save()
    
    settle_bets(round_obj)
    return Response({'status': 'Result declared'})
