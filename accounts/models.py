from django.db import models
from django.conf import settings
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
    

class Article(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()

    image = models.ImageField(
        upload_to="articles/",
        blank=True,
        null=True
    )

    source = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional (e.g. WHO, Mind.org, Adapted)"
    )

    is_curated = models.BooleanField(
        default=True,
        help_text="Curated wellbeing content"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



class Reflection(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    is_anonymous = models.BooleanField(default=False)

    title = models.CharField(max_length=200)
    text = models.TextField()

    image = models.ImageField(
        upload_to="reflections/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def display_name(self):
        return "Anonymous" if self.is_anonymous else self.author.username



class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    reflection = models.ForeignKey(
        Reflection, on_delete=models.CASCADE, related_name="comments"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


