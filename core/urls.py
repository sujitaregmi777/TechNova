from django.urls import path
from core.views.journal_views import journal_list, enter_journal

urlpatterns = [
    path('journal/', journal_list, name='journal_list'),
    path('journal/enter/', enter_journal, name='enter_journal'),
]
