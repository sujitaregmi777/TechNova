from django import views
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from accounts.views import dashboard
from core.views import (
    ai_chat,
    chat_delete,
    chat_list,
    chat_processing,
    delete_podcast,
    enter_journal,
    journal_list,
    journal_create,
    journal_edit,
    journal_delete,
    listen_chat,
    listen_chat,
    listen_podcast,
    new_ai_chat,
    podcast_list,
    podcast_processing,
    save_chat,
    toggle_favorite
)

urlpatterns = [
    path("journals/enter/", enter_journal, name="enter_journal"),
    path("journals/", journal_list, name="journal_list"),
    path("journals/create/", journal_create, name="journal_create"),
    path("journals/edit/<int:pk>/", journal_edit, name="journal_edit"),
    path("journals/delete/<int:pk>/", journal_delete, name="journal_delete"),

    path("dashboard/", dashboard, name="dashboard"),

    path("podcasts/", podcast_list, name="podcast_list"),
    path("podcasts/<int:pk>/", listen_podcast, name="listen_podcast"),

    path("podcast/processing/<int:pk>/", podcast_processing, name="podcast_processing"),
    path("toggle-favorite/<int:id>/", toggle_favorite, name="toggle_favorite"),
    path("delete-podcast/<int:id>/", delete_podcast, name="delete_podcast"),
    path("ai-chats/delete/<int:pk>/", chat_delete, name="chat_delete"),


    path("ai-chat/", chat_list, name="chat_list"),
    path("ai-chat/new/", new_ai_chat, name="new_ai_chat"),
    path("ai-chat/<int:session_id>/", ai_chat, name="ai_chat"),
    path("ai-chat/save/<int:session_id>/", save_chat, name="save_chat"),
    path("ai-chat/processing/<int:pk>/", chat_processing, name="chat_processing"),
    path("ai-chat/listen/<int:pk>/", listen_chat, name="listen_chat")


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)