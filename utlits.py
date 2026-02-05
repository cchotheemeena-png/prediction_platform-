from .models import Bet, GameRound
from wallet.models import Transaction, Wallet

def settle_bets(round_obj):
    for bet in round_obj.bets.all():
        is_winner = _is_winning_bet(bet, round_obj)
        bet.is_winning = is_winner
        
        wallet = bet.user.wallet
        if is_winner:
            winnings = bet.amount * bet.payout_multiplier
            bet.won_amount = winnings
            wallet.locked_balance -= bet.amount
            wallet.main_balance += winnings
            Transaction.objects.create(
                wallet=wallet, amount=winnings, type='bet_won', 
                reference_id=f"bet_{bet.id}"
            )
        else:
            wallet.locked_balance -= bet.amount
        
        wallet.save()
        bet.save()
    
    round_obj.status = 'completed'
    round_obj.save()

def _is_winning_bet(bet, round_obj):
    if bet.bet_type == 'color':
        return bet.selection == round_obj.result_color
    elif bet.bet_type == 'number':
        return int(bet.selection) == round_obj.result_number
    elif bet.bet_type == 'size':
        expected_size = 'big' if round_obj.result_number >= 5 else 'small'
        return bet.selection == expected_size
    return False
