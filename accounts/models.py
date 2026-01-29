from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class EmailOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)

    def __str__(self):
        return f"OTP for {self.user.email}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_guest = models.BooleanField(default=False)
    action_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} | guest={self.is_guest}"



class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="settings")
    
    # Example settings
    email_notifications = models.BooleanField(default=True)
    journals_private = models.BooleanField(default=False)
    dark_mode = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Settings"
