from django.db import models
from django.conf import settings


class Journal(models.Model):

    MOOD_CHOICES = [
        ("happy", "Happy"),
        ("sad", "Sad"),
        ("anxious", "Anxious"),
        ("calm", "Calm"),
        ("grateful", "Grateful"),
        ("overwhelmed", "Overwhelmed"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="journals"
    )

    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title or "Untitled reflection"

class Podcast(models.Model):
    STATUS_CHOICES = [
        ("processing", "Processing"),
        ("ready", "Ready"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="podcasts"
    )

    journal = models.ForeignKey(Journal, on_delete=models.CASCADE)

    title = models.CharField(max_length=200)
    script = models.TextField()
    audio_file = models.FileField(upload_to="podcasts/", blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="processing")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
