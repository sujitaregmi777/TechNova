from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from core.models import Journal, Podcast
from .models import EmailOTP
import uuid,json,os,random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Reflection
from .forms import ReflectionForm, CommentForm,ProfilePhotoForm, StyledPasswordChangeForm
from .utils import check_content,update_streak
from .models import Article, Comment
from django.contrib.auth import update_session_auth_hash
from .models import UserProfile


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


@login_required
def dashboard(request):
    latest_reflection = (
        Journal.objects
        .filter(owner=request.user)
        .order_by("-created_at")
        .first()
    )

    processing_podcast = (
        Podcast.objects
        .filter(owner=request.user, status="processing")
        .order_by("-created_at")
        .first()
    )

    latest_ready = (
        Podcast.objects
        .filter(owner=request.user, status="ready")
        .order_by("-created_at")
        .first()
    )

    latest_podcast = processing_podcast or latest_ready

    streak = getattr(request.user, "userstreak", None)

    return render(
        request,
        "accounts/dashboard.html",
        {
            "latest_reflection": latest_reflection,
            "latest_podcast": latest_podcast,
            "processing": bool(processing_podcast),
            "streak": streak,
        }
    )


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

def settings(request):
    return render(request, "accounts/settings.html")

def reflections_list(request):
    reflections = Reflection.objects.order_by("-created_at")
    return render(request, "accounts/blog/reflections_list.html", {
        "reflections": reflections
    })

@login_required
def reflection_detail(request, pk):
    reflection = get_object_or_404(Reflection, pk=pk)

    return render(request, "accounts/blog/reflection_detail.html", {
        "reflection": reflection,
        "form": CommentForm()
    })



@login_required
def create_reflection(request):
    if request.method == "POST":
        form = ReflectionForm(request.POST)
        if form.is_valid():
            check = check_content(form.cleaned_data["text"])

            if check == "hard":
                messages.error(request, "This post contains harmful language.")
                return redirect("create_reflection")

            reflection = form.save(commit=False)
            reflection.author = request.user
            reflection.save()
            return redirect("reflections_list")
    else:
        form = ReflectionForm()

    return render(request, "accounts/blog/create_reflection.html", {"form": form})

@login_required
def edit_reflection(request, pk):
    reflection = get_object_or_404(Reflection, pk=pk)

    if reflection.author != request.user:
        return redirect("reflection_detail", pk=pk)

    if request.method == "POST":
        form = ReflectionForm(
            request.POST,
            request.FILES,
            instance=reflection
        )
        if form.is_valid():
            form.save()
            return redirect("reflection_detail", pk=pk)
    else:
        form = ReflectionForm(instance=reflection)

    return render(request, "accounts/blog/edit_reflection.html", {
        "form": form,
        "reflection": reflection
    })


@login_required
def add_comment(request, pk):
    reflection = get_object_or_404(Reflection, pk=pk)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]

            check = check_content(content)

            if check == "hard":
                messages.error(
                    request,
                    "This comment wasn’t posted because it may be harmful."
                )
                return redirect("reflection_detail", pk=pk)

            comment = form.save(commit=False)
            comment.author = request.user
            comment.reflection = reflection

            if check == "soft":
                comment.is_approved = True
                messages.warning(
                    request,
                    "Please try to keep responses kind and supportive."
                )
            else:
                comment.is_approved = True

            comment.save()

    return redirect("reflection_detail", pk=pk)


def explore(request):
    articles = Article.objects.order_by("-created_at")
    return render(
        request,
        "accounts/blog/explore.html",
        {"articles": articles}
    )

def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    return render(
        request,
        "accounts/blog/article_detail.html",
        {"article": article}
    )
def blogs(request):
    articles = Article.objects.order_by("-created_at")[:6]
    reflections = Reflection.objects.order_by("-created_at")[:6]

    return render(
        request,
        "accounts/blog/blogs.html",
        {
            "articles": articles,
            "reflections": reflections,
        }
    )

@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    # permission check
    if comment.author != request.user:
        messages.error(request, "You cannot delete this comment.")
        return redirect("reflection_detail", pk=comment.reflection.id)

    if request.method == "POST":
        reflection_id = comment.reflection.id
        comment.delete()
        messages.success(request, "Comment deleted.")
        return redirect("reflection_detail", pk=reflection_id)


    return redirect("reflection_detail", pk=comment.reflection.id)

@login_required
def delete_reflection(request, pk):
    reflection = get_object_or_404(Reflection, pk=pk)

    # Permission check
    if reflection.author != request.user:
        messages.error(request, "You cannot delete this reflection.")
        return redirect("reflection_detail", pk=pk)

    if request.method == "POST":
        reflection.delete()
        messages.success(request, "Reflection deleted.")
        return redirect("reflections_list")

    # Safety fallback
    return redirect("reflection_detail", pk=pk)

@login_required
def settings(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    # Forms
    photo_form = ProfilePhotoForm(instance=profile)
    password_form = StyledPasswordChangeForm(user=request.user)

    if request.method == "POST":

        # PHOTO UPDATE
        if "photo_submit" in request.POST:
            photo_form = ProfilePhotoForm(
                request.POST,
                request.FILES,
                instance=profile
            )
            if photo_form.is_valid():
                photo_form.save()
                messages.success(request, "Profile photo updated successfully.")
                return redirect("settings")

        # PASSWORD CHANGE
        elif "password_submit" in request.POST:
            password_form = StyledPasswordChangeForm(
                user=request.user,
                data=request.POST
            )
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password changed successfully.")
                return redirect("settings")
            
        # DELETE PHOTO
        elif "delete_photo" in request.POST:
            if profile.photo:
        # delete file from storage
                if os.path.isfile(profile.photo.path):
                    os.remove(profile.photo.path)

        profile.photo = None
        profile.save()

        messages.success(request, "Profile photo removed.")
        return redirect("settings")


    context = {
        "photo_form": photo_form,
        "password_form": password_form,
        "profile": profile,
    }
    return render(request, "accounts/settings.html", context)

@login_required
def toggle_reflection_favorite(request, pk):
    reflection = get_object_or_404(Reflection, pk=pk)

    if request.user in reflection.favorites.all():
        reflection.favorites.remove(request.user)
    else:
        reflection.favorites.add(request.user)

    return redirect("reflections_list")




