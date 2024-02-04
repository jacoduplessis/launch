from django import forms

from .models import Project, Action, Comment, Attachment, Risk, Issue, Gap, Decision, ProjectMembership
from django.contrib.auth.models import User

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


class CommentCreateForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = [
            "content_type",
            "object_id",
            "body",
        ]
        widgets = {
            "content_type": forms.HiddenInput(),
            "object_id": forms.HiddenInput(),
            "body": forms.Textarea(attrs={
                "placeholder": "Type here...",
                "class": "form-control-light",
                "rows": 3,
            })
        }
        labels = {
            "body": "Comment",
        }


class AttachmentCreateForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = [
            "content_type",
            "object_id",
            "file",
        ]
        widgets = {
            "content_type": forms.HiddenInput(),
            "object_id": forms.HiddenInput(),
        }
        labels = {
            "file": "Upload Attachment",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["file"].required = True


class ProjectUpdateForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "name",
            "overview",
            "start_date",
            "end_date",
        ]


class ProjectImageForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "image",
        ]

        labels = {
            "image": "Upload Image",
        }


class RiskCreateForm(forms.ModelForm):
    class Meta:
        model = Risk
        fields = [
            "name",
            "description",
            "mitigation",
            "impact",
            "likelihood",
        ]


class IssueCreateForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = [
            "name",
            "description",
            "impact",
        ]


class GapCreateForm(forms.ModelForm):
    class Meta:
        model = Gap
        fields = [
            "name",
            "description",
            "mitigation",
        ]


class DecisionCreateForm(forms.ModelForm):
    class Meta:
        model = Decision
        fields = [
            "name",
            "description",
            "next_steps",
        ]


class ProjectMembershipCreateForm(forms.ModelForm):

    email = forms.EmailField(required=True)

    class Meta:
        model = ProjectMembership
        fields = [
            "role",
        ]

    def save(self, project_id, created_by=None):

        email = self.cleaned_data["email"]

        user, created = User.objects.get_or_create(
            username=email, defaults={"email": email}
        )

        obj = super().save(commit=False)
        obj.user = user
        obj.project_id = project_id
        obj.created_by = created_by
        obj.save()
        return obj


class ProjectMembershipUpdateForm(forms.ModelForm):
    class Meta:
        model = ProjectMembership
        fields = [
            "role",
        ]


class ActionUpdateForm(forms.ModelForm):

    class Meta:
        model = Action
        fields = [
            "name",
            "assigned_to",
            "due_date",
            "priority",
        ]