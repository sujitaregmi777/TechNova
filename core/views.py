from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from moodmate.reflectcast.input.handlers import process_input
from moodmate.reflectcast.nlp.generate_script import create_script



@login_required
def enter_journal(request):
    if request.method == "POST":
        user_text = request.POST.get("reflection")
        user_selected_emotion = request.POST.get("emotion")

        # 1. Save reflection to file system
        reflection_text, filepath = process_input(user_text, "reflection")

        # 2. Generate podcast script using ReflectCast NLP
        script = create_script(
            reflection=reflection_text,
            emotion=user_selected_emotion,
            user_id=str(request.user.id)
        )

        # (Later you'll pass script to audio generator)

        return render(request, "journal/success.html", {
            "script": script,
            "file_path": filepath
        })

    return render(request, "journal/enter_journal.html")
