from django import forms
from .models import Project, Action


class ProjectCreateForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = [
            "name",
            "overview",
            "sponsor",
            "lead",
            "start_date",
            "end_date",
        ]


class ActionCreateForm(forms.ModelForm):

    class Meta:
        model = Action
        fields = [
            "name",
            "description",
            "assigned_to",
            "due_date",
            "priority",
            "sub_tasks",
        ]
