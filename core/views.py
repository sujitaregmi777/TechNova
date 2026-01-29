from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from threading import Thread
from django.http import JsonResponse
from core.utils.filters import apply_common_filters

from core.models import Journal, Podcast
from core.forms import JournalForm
from moodmate.reflectcast.audio.generate_audio import text_to_podcast
from moodmate.reflectcast.audio.mix_audio import mix_voice_with_ambient
from moodmate.reflectcast.input.handlers import process_input
from moodmate.reflectcast.nlp.generate_script import create_script
from moodmate.reflectcast.nlp.generate_title import generate_podcast_title
from .utils import  update_streak



# ---------------------------------------------------
# Background worker for podcast generation
# ---------------------------------------------------

def generate_podcast_assets(podcast_id, journal_content, journal_mood, user_id):
    print(f"[Podcast Worker Started (ID: {podcast_id})]")
    podcast = Podcast.objects.get(id=podcast_id)

    print(f'Generating Title...')
    # Generate title
    title = generate_podcast_title(
        reflection=journal_content,
        emotion=journal_mood
    )
    print(" Generating script ....")
    # Generate script
    script = create_script(
        reflection=journal_content,
        emotion=journal_mood,
        user_id=user_id
    )
    # Audio
    audio_path = text_to_podcast(script)
    
    #Mixing ambient sound
    final_audio_path = mix_voice_with_ambient(
            voice_path=audio_path,
            mood=journal_mood,
            podcast_id=podcast_id
        )

    # Save generated content
    podcast.title = title
    podcast.script = script
    podcast.audio_file = final_audio_path
    podcast.status = "ready"
    podcast.save()


# ---------------------------------------------------
# Journal Input (optional text preprocessing)
# ---------------------------------------------------

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

        return render(request, "core/journal_input.html", {
            "script": script,
            "file_path": filepath
        })

    return render(request, "core/journal_input.html")


# ---------------------------------------------------
# Journal CRUD
# ---------------------------------------------------

@login_required
def journal_list(request):
    journals = Journal.objects.filter(owner=request.user)
    journals = apply_common_filters(journals, request)
    return render(request, "core/journal_list.html", {
        "journals": journals
    })

@login_required
def journal_create(request):
    if request.method == "POST":
        form = JournalForm(request.POST)
        action = request.POST.get("action")

        if form.is_valid():
            journal = form.save(commit=False)
            journal.owner = request.user

            # Auto-generate title if empty
            if not journal.title.strip():
                journal.title = generate_podcast_title(
                    reflection=journal.content,
                    emotion=journal.mood
                )

            journal.save()

            # ✅ STREAK ONLY UPDATES AFTER SUCCESSFUL SAVE
            update_streak(request.user)

            # ---- Case 1: Save only ----
            if action == "save":
                return redirect("journal_list")

            # ---- Case 2: Go to AI chat ----
            if action == "chat":
                request.session["chat_journal_id"] = journal.id
                return redirect("ai_chat")

            # ---- Case 3: Generate podcast ----
            if action == "podcast":
                podcast = Podcast.objects.create(
                    owner=request.user,
                    journal=journal,
                    title="Generating...",
                    script="",
                    status="processing"
                )

                Thread(
                    target=generate_podcast_assets,
                    args=(podcast.id, journal.content, journal.mood, str(request.user.id))
                ).start()

                return redirect("podcast_processing", podcast.id)

    else:
        # ✅ READ mood coming from dashboard
        mood_from_dashboard = request.GET.get("mood")
        form = JournalForm(initial={"mood": mood_from_dashboard})

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


# ---------------------------------------------------
# Podcast Views
# ---------------------------------------------------

@login_required
def podcast_processing(request, pk):
    podcast = get_object_or_404(Podcast, pk=pk, owner=request.user)

    if podcast.status == "ready":
        return redirect("listen_podcast", podcast.id)

    return render(request, "core/podcast_processing.html", {"podcast": podcast})

@login_required
def listen_podcast(request, pk):
    podcast = get_object_or_404(Podcast, pk=pk, owner=request.user)
    return render(request, "core/listen.html", {"podcast": podcast})

@login_required
def toggle_favorite(request, id):
    podcast = get_object_or_404(Podcast, id=id, owner=request.user)
    podcast.favorite = not podcast.favorite
    podcast.save()
    return JsonResponse({"favorite": podcast.favorite})


@login_required
def delete_podcast(request, id):
    Podcast.objects.filter(id=id, owner=request.user).delete()
    return JsonResponse({"deleted": True})

@login_required
def podcast_list(request):
    podcasts = Podcast.objects.filter(
        owner=request.user,
        status="ready"
    )
    podcasts = apply_common_filters(podcasts, request)

    return render(request, "core/podcast_list.html", {
        "podcasts": podcasts
    })

# @login_required
# def chat_list(request):
#     chats = Chat.objects.filter(owner=request.user)
#     chats = apply_common_filters(chats, request)

#     return render(request, "core/chat_list.html", {
#         "chats": chats
#     })

# def ai_chat(request):
#     messages = ChatMessage.objects.filter(user=request.user).order_by("created_at")

#     if request.method == "POST":
#         user_text = request.POST["message"]

#         ChatMessage.objects.create(
#             user=request.user,
#             sender="user",
#             text=user_text
#         )

#         # --- AI response (later connect to Ollama) ---
#         ai_reply = generate_ai_reply(user_text)

#         ChatMessage.objects.create(
#             user=request.user,
#             sender="ai",
#             text=ai_reply
#         )

#         return redirect("ai_chat")

#     return render(request, "ai_chat.html", {"messages": messages})
