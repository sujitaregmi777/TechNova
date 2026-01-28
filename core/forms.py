from django import forms
from .models import Journal

class JournalForm(forms.ModelForm):
    class Meta:
        model = Journal
        fields = ["title", "mood", "content"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": (
                    "w-full rounded-xl p-3 "
                    "bg-[var(--surface-alt)] "
                    "border border-[var(--border)] "
                    "text-[var(--text)] placeholder-[var(--muted)] "
                    "focus:outline-none focus:border-[var(--primary)]"
                ),
                "placeholder": "Title (optional)"
            }),
            "mood": forms.Select(attrs={
                "class": (
                    "w-full rounded-xl p-3 "
                    "bg-[var(--surface-alt)] "
                    "border border-[var(--border)] "
                    "text-[var(--text)] "
                    "focus:outline-none focus:border-[var(--primary)]"
                )
            }),
            "content": forms.Textarea(attrs={
                "class": (
                    "w-full rounded-xl p-4 h-60 "
                    "bg-[var(--surface-alt)] "
                    "border border-[var(--border)] "
                    "text-[var(--text)] placeholder-[var(--muted)] "
                    "focus:outline-none focus:border-[var(--primary)]"
                ),
                "placeholder": "Write your thoughts here..."
            }),
        }
