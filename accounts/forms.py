from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Reflection, Comment

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("email", "username", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget = forms.HiddenInput()
        self.fields["username"].required = False

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-indigo-500 focus:border-indigo-500"
            })

class ReflectionForm(forms.ModelForm):
    class Meta:
        model = Reflection
        fields = ["title", "text", "image", "is_anonymous"]    
        widgets = {
            "title ": forms.TextInput(attrs={
                "placeholder": "Share what’s on your mind…"
            }),
            "text": forms.Textarea(attrs={
                "rows": 8,
                "placeholder": "Write freely…"
            }),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={
                "rows": 2,
                "placeholder": "Respond with kindness…"
            })
        }