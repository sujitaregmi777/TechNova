from django.utils import timezone
from datetime import timedelta
from accounts.models import UserStreak

def update_streak(user):
    streak, _ = UserStreak.objects.get_or_create(user=user)
    today = timezone.now().date()

    if streak.last_checkin == today:
        return

    if streak.last_checkin == today - timedelta(days=1):
        streak.current_streak += 1
    else:
        streak.current_streak = 1

    streak.last_checkin = today
    streak.save()
