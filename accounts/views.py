from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login
from django.contrib import messages
from .forms import RegisterForm
import random,uuid
from django.core.mail import send_mail
from django.conf import settings
from .models import LoginOTP
# from .utils import generate_otp
from django.contrib.auth.models import User

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email   
            user.save()

            login(request, user)
            return redirect("dashboard")
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html")

def generate_otp():
    return str(random.randint(100000, 999999))

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(username=email)
        except User.DoesNotExist:
            messages.error(request, "Invalid credentials")
            return redirect("login")

        user = authenticate(request, username=email, password=password)

        if not user:
            messages.error(request, "Invalid credentials")
            return redirect("login")

        otp = generate_otp()
        LoginOTP.objects.create(user=user, code=otp)

        send_mail(
            subject="MoodMate Login OTP",
            message=f"Your OTP is {otp}. It expires in 5 minutes.",
            from_email="no-reply@moodmate.local",
            recipient_list=[user.email],
        )

        request.session["otp_user_id"] = user.id
        messages.success(request, "OTP sent to your email")
        return redirect("verify_otp")

    return render(request, "accounts/login.html")

def verify_otp(request):
    user_id = request.session.get("otp_user_id")

    if not user_id:
        return redirect("login")

    if request.method == "POST":
        otp_input = request.POST.get("otp")

        otp_obj = LoginOTP.objects.filter(
            user_id=user_id,
            code=otp_input,
            is_used=False
        ).last()

        if not otp_obj or otp_obj.is_expired():
            messages.error(request, "Invalid or expired OTP")
            return redirect("verify_otp")

        otp_obj.is_used = True
        otp_obj.save()

        login(request, otp_obj.user)
        del request.session["otp_user_id"]

        return redirect("dashboard")

    return render(request, "accounts/verify_otp.html")


