HARD_BLOCK = [
    "kill yourself",
    "you should die",
    "i will kill",
]

SOFT_BLOCK = [
    "stupid",
    "idiot",
    "your fault",
]

def check_content(text):
    text = text.lower()

    if any(word in text for word in HARD_BLOCK):
        return "hard"

    if any(word in text for word in SOFT_BLOCK):
        return "soft"

    return "ok"

from django.utils import timezone
from datetime import timedelta
from .models import UserStreak

def update_streak(user):
    today = timezone.now().date()
    streak, _ = UserStreak.objects.get_or_create(user=user)

    if streak.last_checkin == today:
        return streak  # already counted today

    if streak.last_checkin == today - timedelta(days=1):
        streak.current_streak += 1
    else:
        streak.current_streak = 1

    streak.last_checkin = today
    streak.longest_streak = max(
        streak.longest_streak,
        streak.current_streak
    )
    streak.save()
    return streak

