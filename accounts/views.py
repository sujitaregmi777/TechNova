from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import EmailOTP
from django.contrib import messages
from .forms import CustomUserCreationForm
import random,uuid
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.conf import settings

def register(request):
    if request.method == "POST":
        data = request.POST.copy()
        email = data.get("email")

        if email:
            data["username"] = email

        form = CustomUserCreationForm(data)
        print("REGISTER VIEW HIT")
        if form.is_valid():
            user = form.save(commit=False)

            user.email = email
            user.username = email

            user.is_active = False
            user.save()

            otp = generate_otp()
            EmailOTP.objects.create(user=user, otp=otp)

            

            send_mail(
                subject="Verify your Moodmate account",
                message=f"Your OTP is {otp}",
                from_email="no-reply@moodmate.com",
                recipient_list=[user.email],
            )

            request.session["otp_user_id"] = user.id

            messages.success(
                request,
                "We have sent a verification code to your email."
            )

            return redirect("verify_otp")

    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/register.html", {"form": form})

def generate_otp():
    return str(random.randint(100000, 999999))

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user is None:
            messages.error(request, "Invalid email or password.")
            return render(request, "accounts/login.html")

        if not user.is_active:
            messages.error(
                request,
                "Your account is not verified. Please verify your email."
            )
            return render(request, "accounts/login.html")

        auth_login(request, user)
        print(request.POST)
        messages.success(request, "Welcome back!")
        return redirect("dashboard")  # must exist

    return render(request, "accounts/login.html")

def verify_otp(request):
    user_id = request.session.get("otp_user_id")

    if not user_id:
        return redirect("login")

    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        entered_otp = request.POST.get("otp")

        try:
            otp_obj = EmailOTP.objects.get(user=user)
        except EmailOTP.DoesNotExist:
            messages.error(request, "OTP expired or invalid.")
            return redirect("register")

        if entered_otp == otp_obj.otp:
            otp_obj.delete()  

            user.is_active = True
            user.save()

            del request.session["otp_user_id"]
            auth_login(request, user)

            messages.success(request, "Email verified successfully!")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid OTP. Try again.")

    return render(request, "accounts/verify_otp.html")

def resend_otp(request):
    user_id = request.session.get("otp_user_id")

    if not user_id:
        messages.error(request, "Session expired. Please register again.")
        return redirect("register")

    user = get_object_or_404(User, id=user_id)

    # Delete old OTP if exists
    EmailOTP.objects.filter(user=user).delete()

    # Generate new OTP
    otp = generate_otp()
    EmailOTP.objects.create(user=user, otp=otp)

    send_mail(
        subject="Your new MoodMate verification code",
        message=f"Your new OTP is {otp}",
        from_email="no-reply@moodmate.com",
        recipient_list=[user.email],
    )

    messages.success(request, "A new verification code has been sent to your email.")
    return redirect("verify_otp")

@login_required
def dashboard(request):
    return render (request, "accounts/dashboard.html")
