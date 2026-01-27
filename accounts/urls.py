# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path('login/', views.login_view, name='login'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path("dashboard/", views.dashboard, name="dashboard"),
     path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset/password_reset.html",
            email_template_name="accounts/password_reset/password_reset_email.html",
            subject_template_name="accounts/password_reset/password_reset_subject.txt",
            success_url="password_reset /password-reset/done/"
        ),
        name="password_reset"
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset/password_reset_done.html"
        ),
        name="password_reset_done"
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset/password_reset_confirm.html",
            success_url="/reset/done/"
        ),
        name="password_reset_confirm"
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset/password_reset_complete.html"
        ),
        name="password_reset_complete"
    ),
    path("set-mood/", views.set_mood, name="set_mood"),
    path("breathing/", views.breathing, name="breathing"),
    path("explore/", views.explore, name="explore"),
    path("reflections/", views.reflections, name="reflections"),
]


