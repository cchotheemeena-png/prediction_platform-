from django.db import models, transaction
from django.db.models import Sum
from django.utils import timezone
from decimal import Decimal
from core.models import TimestampedModel, User
from wallet.models import Wallet

class GameRound(TimestampedModel):
    round_id = models.PositiveIntegerField(unique=True)
    status = models.CharField(max_length=20, choices=[
        ('waiting', 'Waiting'), ('active', 'Active'), 
        ('locked', 'Locked'), ('settled', 'Settled'), ('completed', 'Completed')
    ], default='waiting')
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    result_color = models.CharField(max_length=10, blank=True, null=True)
    result_number = models.IntegerField(blank=True, null=True)
    result_size = models.CharField(max_length=10, blank=True, null=True)
    
    @property
    def seconds_remaining(self):
        now = timezone.now()
        if now >= self.ends_at:
            return 0
        return max(0, int((self.ends_at - now).total_seconds()))
    
    @property
    def is_active(self):
        now = timezone.now()
        return self.starts_at <= now <= self.ends_at

class Bet(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    round = models.ForeignKey(GameRound, on_delete=models.CASCADE, related_name='bets')
    bet_type = models.CharField(max_length=10, choices=[('color','Color'),('number','Number'),('size','Size')])
    selection = models.CharField(max_length=20)  # 'red', '5', 'big'
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payout_multiplier = models.DecimalField(max_digits=5, decimal_places=3, default=2.0)
    is_winning = models.BooleanField(default=False)
    won_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'round'], name='unique_user_round')]
