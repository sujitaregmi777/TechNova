from django.urls import path
from accounts.views import dashboard
from core.views import (
    enter_journal,
    journal_list,
    journal_create,
    journal_edit,
    journal_delete,
    listen_podcast,
    podcast_list,
    podcast_processing
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
]
