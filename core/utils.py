from django.utils import timezone
from datetime import timedelta
from .models import UserStreak

def update_streak(user):
    streak, created = UserStreak.objects.get_or_create(user=user)
    today = timezone.now().date()

    # Already updated today → do nothing
    if streak.last_check_in == today:
        return

    # Consecutive day → increment
    if streak.last_check_in == today - timedelta(days=1):
        streak.current_streak += 1
    else:
        # First time or break → reset to 1
        streak.current_streak = 1

    streak.last_check_in = today
    streak.save()
