from django.db import models
from django.db.models import Sum
from decimal import Decimal
import uuid
from core.models import User, TimestampedModel

class Wallet(TimestampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    main_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    locked_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    @property
    def total_balance(self):
        return self.main_balance + self.locked_balance
    
    def can_withdraw(self, amount):
        return self.main_balance >= amount and not self.user.wallet_frozen

class Transaction(TimestampedModel):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    tx_id = models.UUIDField(default=uuid.uuid4, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.CharField(max_length=20, choices=[
        ('deposit', 'Deposit'), ('withdrawal', 'Withdrawal'),
        ('bet_placed', 'Bet Placed'), ('bet_won', 'Bet Won')
    ])
    status = models.CharField(max_length=20, default='completed')

class WithdrawalRequest(TimestampedModel):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')
