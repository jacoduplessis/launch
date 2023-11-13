from django import forms

from .models import Project, Action, Comment, Attachment


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
                "placeholder": "Type here..."
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
