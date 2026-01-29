# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("", views.index, name="index"),
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
    path("comments/<int:pk>/delete/",views.delete_comment,name="delete_comment"),

    path("set-mood/", views.set_mood, name="set_mood"),
    path("breathing/", views.breathing, name="breathing"),
    path("settings/", views.settings, name="settings"),
    path("reflections/", views.reflections_list, name="reflections_list"),
    path("reflections/new/", views.create_reflection, name="create_reflection"),
    path("reflections/<int:pk>/", views.reflection_detail, name="reflection_detail"),
    path("reflections/<int:pk>/edit/", views.edit_reflection, name="edit_reflection"),
    path("reflections/<int:pk>/comment/", views.add_comment, name="add_comment"),
    path("explore/", views.explore, name="explore"),
    path("read/<int:pk>/", views.article_detail, name="article_detail"),
    path("blogs/", views.blogs, name="blogs"),
    path("reflections/<int:pk>/delete/",views.delete_reflection,name="delete_reflection"),
    path(
  "reflections/<int:pk>/favorite/",
  views.toggle_reflection_favorite,
  name="toggle_reflection_favorite"
),


    



]

