from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from threading import Thread
from django.http import JsonResponse
from core.utils.filters import apply_common_filters

from core.models import ChatMessage, ChatPodcast, ChatSession, Journal, Podcast
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

@login_required
def chat_list(request):
    chats = ChatSession.objects.filter(owner=request.user)
    chats = apply_common_filters(chats, request)

#     return render(request, "core/chat_list.html", {
#         "chats": chats
#     })

def generate_ai_reply_from_chat(session, user_text, user_id):
    """
    Uses existing LLM script generator to produce next AI question
    """

    # Build conversation so far
    conversation = "\n".join(
        f"{m.sender.upper()}: {m.text}"
        for m in session.messages.order_by("created_at")
    )

    # Prompt instructing LLM to ask next deep question
    prompt = f"""
You are an empathetic AI companion helping a user reflect.
Your goal is to ask ONE thoughtful follow-up question that helps understand the user deeper.
Do NOT give advice yet. Only ask one question.

Conversation so far:
{conversation}

User just said:
{user_text}

Ask the next question:
"""

    ai_question = create_script(
        reflection=prompt,
        emotion="reflective",
        user_id=user_id
    )

    return ai_question.strip()

@login_required
def new_ai_chat(request):
    session = ChatSession.objects.create(owner=request.user)

    ChatMessage.objects.create(
        session=session,
        sender="ai",
        text="Hello! I'm here to listen and help you reflect. How are you feeling today?"
    )

    return redirect("ai_chat", session_id=session.id)

@login_required
def ai_chat(request, session_id):
    session = get_object_or_404(ChatSession, id=session_id, owner=request.user)
    messages = session.messages.order_by("created_at")

#     if request.method == "POST":
#         user_text = request.POST["message"]

    ChatMessage.objects.create(
            session=session,
            sender="user",
            text=user_text
        )

        ai_reply = generate_ai_reply_from_chat(
            session=session,
            user_text=user_text,
            user_id=str(request.user.id)
        )

        ChatMessage.objects.create(
            session=session,
            sender="ai",
            text=ai_reply
        )

        return redirect("ai_chat", session_id=session.id)

    return render(request, "core/chat_input.html", {
        "messages": messages,
        "session": session
    })

def generate_chat_podcast_assets(chat_podcast_id, conversation_text, user_id):
    chat_podcast = ChatPodcast.objects.get(id=chat_podcast_id)

    print("Generating chat-based title...")
    title = generate_podcast_title(
        reflection=conversation_text,
        emotion="reflective"
    )

    print("Generating chat-based script...")
    script = create_script(
        reflection=conversation_text,
        emotion="reflective",
        user_id=user_id
    )

    audio_path = text_to_podcast(script)

    final_audio_path = mix_voice_with_ambient(
        voice_path=audio_path,
        mood="calm",
        podcast_id=chat_podcast_id
    )

    chat_podcast.title = title
    chat_podcast.script = script
    chat_podcast.audio_file = final_audio_path
    chat_podcast.status = "ready"
    chat_podcast.save()

@login_required
def save_chat(request, session_id):
    session = get_object_or_404(ChatSession, id=session_id, owner=request.user)
    session.completed = True
    session.save()

    # Collect full conversation text
    conversation = "\n".join(
        f"{m.sender.upper()}: {m.text}"
        for m in session.messages.order_by("created_at")
    )

    # Create ChatPodcast record
    chat_podcast = ChatPodcast.objects.create(
        owner=request.user,
        session=session,
        title="Generating...",
        script="",
        status="processing"
    )

    # Start background worker using your existing pipeline
    Thread(
        target=generate_chat_podcast_assets,
        args=(chat_podcast.id, conversation, str(request.user.id))
    ).start()

    # Reuse SAME processing screen as journals
    return redirect("chat_processing", chat_podcast.id)



@login_required
def chat_processing(request, pk):
    chat_podcast = get_object_or_404(ChatPodcast, pk=pk, owner=request.user)

    if chat_podcast.status == "ready":
        return render(request, "core/podcast_processing.html", {
            "podcast": chat_podcast
        })
    
@login_required
def listen_chat(request, pk):
    chat_podcast = get_object_or_404(ChatPodcast, pk=pk, owner=request.user)
    return render(request, "core/listen.html", {"podcast": chat_podcast})

@login_required
def chat_delete(request, pk):
    chat = get_object_or_404(ChatSession, pk=pk, owner=request.user)

    if request.method == "POST":
        chat.delete()
        return redirect("chat_list")

    return render(request, "core/chat_delete.html", {"chat": chat})
