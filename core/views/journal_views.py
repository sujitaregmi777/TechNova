from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.models import Journal

@login_required
def journal_list(request):
    journals = Journal.objects.filter(user=request.user)
    return render(request, 'core/journal_list.html', {'journals': journals})


@login_required
def enter_journal(request):
    return render(request, 'core/enter_journal.html')
