import mimetypes
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Prefetch, Count
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.contrib.auth.views import LoginView as BaseLoginView, LogoutView as BaseLogoutView
from django.template.defaulttags import lorem
from django.urls import reverse
from django.contrib import messages
from django.utils.lorem_ipsum import paragraphs, words
from django.utils.timezone import now
from django.views.decorators.http import require_POST

from launch.forms import ProjectCreateForm, ActionCreateForm, CommentCreateForm, AttachmentCreateForm
from launch.models import Project, OrganisationMembership, Action, Comment, Attachment


class LoginView(BaseLoginView):
    template_name = "launch/login.html"
    redirect_authenticated_user = True


class LogoutView(BaseLogoutView):
    template_name = "launch/logout.html"


@login_required
def project_list(request):
    context = {
        "breadcrumbs": (
            ("Launch", "/"),
            ("Projects", reverse("project_list")),
            ("List", None)
        ),
        "projects": Project.objects.filter(created_by_id=request.user.id).annotate(
            num_actions=Count("actions"),
            num_comments=Count("comments"),
            num_attachments=Count("attachments"),
        )
    }
    return render(request, template_name="launch/project_list.html", context=context)


def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("dashboard_index"))
    return HttpResponseRedirect(reverse("login"))


@login_required()
def project_create(request):
    context = {
        "breadcrumbs": (
            ("Launch", "/"),
            ("Projects", reverse("project_list")),
            ("Create", None)
        )
    }

    if request.method == "GET":
        context["form"] = ProjectCreateForm(
            initial={
                "name": words(count=6, common=False),
                "overview": "\n\n".join(paragraphs(count=4, common=False)),
                "start_date": now(),
                "end_date": now() + timedelta(days=180)
            }
        )
        return render(request, "launch/project_create.html", context=context)

    if request.method == "POST":
        form = ProjectCreateForm(request.POST, request.FILES)

        if not form.is_valid():
            context["form"] = form
            return render(request, "launch/project_create.html", context=context)

        obj = form.save(commit=False)
        obj.created_by = request.user

        # todo: refine
        user_org_membership = OrganisationMembership.objects.filter(user_id=request.user).first()
        org_id = 1 if user_org_membership is None else user_org_membership.organisation_id
        obj.organisation_id = org_id
        obj.save()

        messages.success(request, "Project has been created.")
        return HttpResponseRedirect(
            reverse("project_detail", args=[obj.pk])
        )


@login_required
def project_detail(request, pk):
    comments_prefetch = Prefetch(
        "comments",
        queryset=Comment.objects.select_related("created_by").order_by("time_created"),
    )

    attachments_prefetch = Prefetch(
        "attachments",
        queryset=Attachment.objects.select_related("created_by")
    )

    qs = Project.objects.prefetch_related(comments_prefetch, attachments_prefetch)
    project = get_object_or_404(qs, pk=pk)
    context = {
        "project": project,
        "breadcrumbs": (
            ("Launch", "/"),
            ("Projects", reverse("project_list")),
            ("Detail", None)
        ),
        "comment_form": CommentCreateForm(
            initial={
                "content_type": ContentType.objects.get_for_model(Project),
                "object_id": project.pk,
            }
        ),
        "attachment_form": AttachmentCreateForm(
            initial={
                "content_type": ContentType.objects.get_for_model(Project),
                "object_id": project.pk,
            }
        )
    }
    return render(request, "launch/project_detail.html", context)


@login_required
def action_list(request, pk):
    actions_prefetch = Prefetch("actions", Action.objects.all())

    project = get_object_or_404(Project.objects.prefetch_related(
        actions_prefetch
    ), pk=pk)

    context = {
        "project": project,
        "actions": project.actions.all(),
        "breadcrumbs": (
            ("Launch", "/"),
            ("Projects", reverse("project_list")),
            (project.name, reverse("project_detail", args=[project.pk])),
            ("Actions", None),
        )
    }

    return render(request, "launch/action_list.html", context)


@login_required()
def action_create(request, pk):
    project = get_object_or_404(Project.objects.all(), pk=pk)

    context = {
        "breadcrumbs": (
            ("Launch", "/"),
            ("Projects", reverse("project_list")),
            (project.name, reverse("project_detail", args=[project.pk])),
            ("Actions", reverse("action_list", args=[project.pk])),
            ("Create", None)
        )
    }

    if request.method == "GET":
        context["form"] = ActionCreateForm(
            initial={
                "name": words(count=6, common=False),
                "description": "\n\n".join(paragraphs(count=4, common=False)),
                "due_date": now() + timedelta(days=30),
            }
        )
        return render(request, "launch/action_create.html", context=context)

    if request.method == "POST":
        form = ActionCreateForm(request.POST, request.FILES)

        if not form.is_valid():
            context["form"] = form
            return render(request, "launch/action_create.html", context=context)

        obj = form.save(commit=False)
        obj.created_by = request.user
        obj.project = project
        obj.save()

        messages.success(request, "Action has been created.")
        return HttpResponseRedirect(
            reverse("action_list", args=[project.pk])
        )


@login_required
def action_detail(request, pk):
    action = get_object_or_404(Action, pk=pk)

    context = {
        "action": action,
    }

    return render(request, "launch/action_detail.html", context=context)


@require_POST
@login_required
def comment_create(request):
    form = CommentCreateForm(request.POST, request.FILES)

    if not form.is_valid():
        return HttpResponseBadRequest()

    comment = form.save(commit=False)
    comment.created_by = request.user
    comment.save()

    next_url = request.POST.get("next")
    if next_url:
        return HttpResponseRedirect(next_url)

    return HttpResponse("OK")


@require_POST
@login_required
def attachment_create(request):
    form = AttachmentCreateForm(request.POST, request.FILES)

    if not form.is_valid():
        return HttpResponseBadRequest()

    attachment = form.save(commit=False)
    uploaded_file = request.FILES['file']
    attachment.size = uploaded_file.size
    mime_type, encoding = mimetypes.guess_type(uploaded_file.name)
    attachment.mime_type = mime_type
    attachment.created_by = request.user
    attachment.save()

    next_url = request.POST.get("next")
    if next_url:
        return HttpResponseRedirect(next_url)

    return HttpResponse("OK")