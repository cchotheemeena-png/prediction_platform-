from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from game.models import GameRound, Bet
from django.db.models import Sum, Count

class AdminDashboard(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        active_round = GameRound.objects.filter(status__in=['active','locked']).first()
        if active_round:
            bets = Bet.objects.filter(round=active_round)
            summary = {
                'total_bets': bets.count(),
                'total_amount': bets.aggregate(Sum('amount'))['amount__sum'] or 0,
                'by_color': {
                    'red': bets.filter(bet_type='color', selection='red').aggregate(Sum('amount'))['amount__sum'] or 0,
                    'green': bets.filter(bet_type='color', selection='green').aggregate(Sum('amount'))['amount__sum'] or 0,
                    'violet': bets.filter(bet_type='color', selection='violet').aggregate(Sum('amount'))['amount__sum'] or 0,
                }
            }
            return Response({'round': active_round.id, 'summary': summary, 'bets': list(bets.values())})
        return Response({'message': 'No active round'})
