from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import RegisterForm

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email   # email as username
            user.save()

            login(request, user)
            return redirect("dashboard")
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html")

