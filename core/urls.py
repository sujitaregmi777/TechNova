from django.urls import path
from core.views import (
    enter_journal,
    journal_list,
    journal_create,
    journal_edit,
    journal_delete
)

urlpatterns = [
    path("journal/enter/", enter_journal, name="enter_journal"),
    path("journal/", journal_list, name="journal_list"),
    path("journal/create/", journal_create, name="journal_create"),
    path("journal/edit/<int:pk>/", journal_edit, name="journal_edit"),
    path("journal/delete/<int:pk>/", journal_delete, name="journal_delete"),
]
