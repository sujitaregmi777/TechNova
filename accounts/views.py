from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from .models import EmailOTP
import random
import uuid
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def index(request):
    reviews = [
        {
            "text": "MoodMate helps me understand my emotions better every day. The mood-based suggestions are calming.",
            "name": "Sarah Thompson",
            "role": "Wellness App User",
        },
        {
            "text": "After long workdays, MoodMate helps me pause and reflect. It’s simple, supportive, and easy to use.",
            "name": "Michael Rodriguez",
            "role": "Busy Professional",
        },
        {
            "text": "I really like how MoodMate adapts based on how I’m feeling. It feels personal and comforting.",
            "name": "Emily Chen",
            "role": "Student",
        },
    ]
    return render(request, "accounts/index.html", {"reviews": reviews})


def generate_otp():
    return str(random.randint(100000, 999999))


def register(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if not email or not password1 or not password2:
            messages.error(request, "All fields are required.")
            return render(request, "accounts/register.html")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, "accounts/register.html")

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, "accounts/register.html")

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password1,
            is_active=False,
        )

        otp = generate_otp()
        EmailOTP.objects.update_or_create(user=user, defaults={"otp": otp})

        send_mail(
            subject="Moodmate – Verify Your Account",
            message=f"Your verification OTP is {otp}.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        request.session["otp_user_id"] = user.id
        messages.success(request, "OTP sent to your email.")
        return redirect("verify_otp")

    return render(request, "accounts/register.html")


def verify_otp(request):
    user_id = request.session.get("otp_user_id")
    if not user_id:
        messages.error(request, "Session expired. Please register again.")
        return redirect("register")

    if request.method == "POST":
        otp_input = request.POST.get("otp")

        try:
            otp_obj = EmailOTP.objects.get(user_id=user_id)
        except EmailOTP.DoesNotExist:
            messages.error(request, "OTP not found.")
            return redirect("register")

        if otp_obj.otp != otp_input:
            messages.error(request, "Invalid OTP.")
            return render(request, "accounts/verify_otp.html")

        user = otp_obj.user
        user.is_active = True
        user.save()

        auth_login(request, user, backend="django.contrib.auth.backends.ModelBackend")

        otp_obj.delete()
        request.session.pop("otp_user_id", None)

        messages.success(request, "Account verified successfully.")
        return redirect("dashboard")

    return render(request, "accounts/verify_otp.html")


def resend_otp(request):
    user_id = request.session.get("otp_user_id")
    if not user_id:
        messages.error(request, "Session expired. Please register again.")
        return redirect("register")

    user = get_object_or_404(User, id=user_id)

    EmailOTP.objects.filter(user=user).delete()

    otp = generate_otp()
    EmailOTP.objects.create(user=user, otp=otp)

    send_mail(
        subject="Moodmate – New Verification Code",
        message=f"Your new OTP is {otp}.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

    messages.success(request, "A new OTP has been sent to your email.")
    return redirect("verify_otp")


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user is None:
            messages.error(request, "Invalid email or password.")
            return render(request, "accounts/login.html")

        if not user.is_active:
            messages.error(request, "Please verify your email first.")
            return redirect("verify_otp")

        auth_login(request, user)
        messages.success(request, "Welcome back!")
        return redirect("dashboard")

    return render(request, "accounts/login.html")



def guest_login(request):
    username = f"guest_{uuid.uuid4().hex[:10]}"
    user = User.objects.create_user(username=username)
    user.set_unusable_password()
    user.save()

    auth_login(
        request,
        user,
        backend="django.contrib.auth.backends.ModelBackend"
    )

    return redirect("dashboard")

@login_required
def dashboard(request):
    return render (request, "accounts/dashboard.html")

def index(request):
    reviews = [
        {
            "text": "MoodMate helps me understand my emotions better every day. The mood-based suggestions are calming.",
            "name": "Sarah Thompson",
            "role": "Wellness App User",
        },
        {
            "text": "After long workdays, MoodMate helps me pause and reflect. It’s simple, supportive, and easy to use.",
            "name": "Michael Rodriguez",
            "role": "Busy Professional",
        },
        {
            "text": "I really like how MoodMate adapts based on how I’m feeling. It feels personal and comforting.",
            "name": "Emily Chen",
            "role": "Student",
        },
    ]

    return render(request, "accounts/index.html", {
        "reviews": reviews
    })


@csrf_exempt
@login_required
def set_mood(request):
    if request.method == "POST":
        data = json.loads(request.body)
        request.session["current_mood"] = data.get("mood")
        return JsonResponse({"status": "ok"})

    return JsonResponse({"status": "invalid"}, status=400)
    

def breathing(request):
    return render(request, "accounts/breathing.html")



