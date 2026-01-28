from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from core.models import Journal
from core.forms import JournalForm   # you should already have this

from moodmate.reflectcast.input.handlers import process_input
from moodmate.reflectcast.nlp.generate_script import create_script


# ----------------------------
# ReflectCast Journal Input
# ----------------------------
@login_required
def enter_journal(request):
    if request.method == "POST":
        user_text = request.POST.get("reflection")
        user_selected_emotion = request.POST.get("emotion")

        # Save reflection text file
        reflection_text, filepath = process_input(user_text, "reflection")

        # Generate podcast script
        script = create_script(
            reflection=reflection_text,
            emotion=user_selected_emotion,
            user_id=str(request.user.id)
        )

        return render(request, "core/journal_input.html", {
            "script": script,
            "file_path": filepath
        })

    return render(request, "core/journal_input.html")


# ----------------------------
# Journal CRUD Views
# ----------------------------
@login_required
def journal_list(request):
    journals = Journal.objects.filter(owner=request.user).order_by("-created_at")
    return render(request, "core/journal_list.html", {"journals": journals})


@login_required
def journal_create(request):
    if request.method == "POST":
        form = JournalForm(request.POST)
        if form.is_valid():
            journal = form.save(commit=False)
            journal.owner = request.user
            journal.save()
            return redirect("journal_list")
    else:
        form = JournalForm()

    return render(request, "core/journal_input.html", {"form": form})


@login_required
def journal_edit(request, pk):
    journal = get_object_or_404(Journal, pk=pk, owner=request.user)

    if request.method == "POST":
        form = JournalForm(request.POST, instance=journal)
        if form.is_valid():
            form.save()
            return redirect("journal_list")
    else:
        form = JournalForm(instance=journal)

    return render(request, "core/journal_input.html", {"form": form})


@login_required
def journal_delete(request, pk):
    journal = get_object_or_404(Journal, pk=pk, owner=request.user)

    if request.method == "POST":
        journal.delete()
        return redirect("journal_list")

    return render(request, "core/delete.html", {"journal": journal})
