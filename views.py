from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from .models import Wallet, Transaction, WithdrawalRequest
from decimal import Decimal

class WalletBalanceView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        wallet = request.user.wallet
        return Response({
            'main_balance': str(wallet.main_balance),
            'locked_balance': str(wallet.locked_balance),
            'total_balance': str(wallet.total_balance)
        })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_withdrawal(request):
    amount = Decimal(request.data['amount'])
    wallet = request.user.wallet
    
    if not wallet.can_withdraw(amount):
        return Response({'error': 'Insufficient balance'}, status=400)
    
    WithdrawalRequest.objects.create(wallet=wallet, amount=amount)
    return Response({'message': 'Withdrawal requested'})
