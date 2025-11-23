from django import forms
from django.apps import apps

Comment = apps.get_model("article", "Comment")


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['display_name', 'content',]
        widget = {
            "display_name": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }
