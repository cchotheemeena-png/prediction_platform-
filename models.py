from django.db import models
from core.models import User, TimestampedModel
import random
import string

class OTP(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=6)
    channel = models.CharField(max_length=10, choices=[('email', 'Email'), ('phone', 'Phone')])
    is_used = models.BooleanField(default=False)
    
    def generate_otp(self):
        self.key = ''.join(random.choices(string.digits, k=6))
