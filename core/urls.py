from django.urls import path
from core.views.journal_views import journal_list, enter_journal
# from core.views.views import index

urlpatterns = [
    path('journal/', journal_list, name='journal_list'),
    path('journal/enter/', enter_journal, name='enter_journal'),

]
