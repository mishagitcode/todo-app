from django import forms
from app.models import Task, Tag


class DateTimeInput(forms.DateTimeInput):
    input_type = "datetime-local"


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["content", "deadline", "tags"]
        widgets = {
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "deadline": DateTimeInput(attrs={"class": "form-control"}),
            "tags": forms.CheckboxSelectMultiple(),
        }


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
        }
