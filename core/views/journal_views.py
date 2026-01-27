from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from core.models import Journal
from moodmate.reflectcast.input.handlers import process_input
from moodmate.reflectcast.nlp.generate_script import create_script


@login_required
def journal_list(request):
    journals = Journal.objects.filter(user=request.user).order_by("-created_at")

    return render(request, "journal/journal_list.html", {
        "journals": journals
    })


@login_required
def enter_journal(request):
    if request.method == "POST":
        user_text = request.POST.get("reflection")
        user_selected_emotion = request.POST.get("emotion")

        reflection_text, filepath = process_input(user_text, "reflection")

        script = create_script(
            reflection=reflection_text,
            emotion=user_selected_emotion,
            user_id=str(request.user.id)
        )

        return render(request, "journal/success.html", {
            "script": script,
            "file_path": filepath
        })

    return render(request, "journal/enter_journal.html")
