import mimetypes
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Prefetch, Count
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.contrib.auth.views import LoginView as BaseLoginView, LogoutView as BaseLogoutView
from django.urls import reverse
from django.contrib import messages
from django.utils.lorem_ipsum import paragraphs, words
from django.utils.timezone import now
from django.views.decorators.http import require_POST

from launch.forms import ProjectCreateForm, ActionCreateForm, CommentCreateForm, AttachmentCreateForm, ProjectUpdateForm, ProjectImageForm, RiskCreateForm, IssueCreateForm, DecisionCreateForm, GapCreateForm, ProjectMembershipCreateForm, ProjectMembershipUpdateForm, ActionUpdateForm
from launch.models import Project, OrganisationMembership, Action, Comment, Attachment, Issue, Decision, Gap, ProjectMembership


class LoginView(BaseLoginView):
    template_name = "launch/login.html"
    redirect_authenticated_user = True


class LogoutView(BaseLogoutView):
    template_name = "launch/logout.html"


@login_required
def project_list(request):
    members_prefetch = Prefetch("members", queryset=ProjectMembership.objects.select_related("user"))

    context = {
        "breadcrumbs": (
            ("Launch", "/"),
            ("Projects", reverse("project_list")),
            ("List", None)
        ),
        "projects": Project.objects.filter(created_by_id=request.user.id).annotate(
            num_actions=Count("actions", distinct=True),
            num_comments=Count("comments", distinct=True),
            num_attachments=Count("attachments", distinct=True),
        ).prefetch_related(members_prefetch)
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

    members_prefetch = Prefetch("members", queryset=ProjectMembership.objects.select_related("user"))
    qs = Project.objects.prefetch_related(comments_prefetch, attachments_prefetch, members_prefetch)
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
        ),
        "image_form": ProjectImageForm()
    }
    return render(request, "launch/project_detail.html", context)


@login_required
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == "GET":
        context = {
            "form": ProjectUpdateForm(instance=project),
            "project": project,
        }

        return render(request, "launch/project_update.html", context)

    if request.method == "POST":

        form = ProjectUpdateForm(request.POST, request.FILES, instance=project)
        if not form.is_valid():
            context = {"form": form, "project": project}
            return render(request, "launch/project_update.html", context)
        form.save()
        messages.success(request, "Project updated.")
        return HttpResponseRedirect(
            reverse("project_detail", args=[project.pk])
        )


@require_POST
@login_required
def project_image(request, pk):
    project = get_object_or_404(Project, pk=pk)

    form = ProjectImageForm(request.POST, request.FILES, instance=project)
    if not form.is_valid():
        messages.error(request, "Error processing image.")
    else:
        form.save()
    return HttpResponseRedirect(
        reverse("project_detail", args=[project.pk])
    )


@login_required
def project_members(request, pk):

    if request.method == "GET":
        members_prefetch = Prefetch("members", queryset=ProjectMembership.objects.select_related("user"))

        project = get_object_or_404(Project.objects.prefetch_related(members_prefetch), pk=pk)

        context = {
            "project": project,
            "form": ProjectMembershipCreateForm(),
            "breadcrumbs": (
                ("Launch", "/"),
                ("Projects", reverse("project_list")),
                (project.name, reverse("project_detail", args=[project.pk])),
                ("Members", None)
            ),
        }

        return render(request, "launch/project_members.html", context=context)

    if request.method == "POST":

        project = get_object_or_404(Project, id=pk)

        form = ProjectMembershipCreateForm(request.POST, request.FILES)

        if not form.is_valid():
            context = {
                "project": project,
                "form": form,
                "breadcrumbs": (
                    ("Launch", "/"),
                    ("Projects", reverse("project_list")),
                    (project.name, reverse("project_detail", args=[project.pk])),
                    ("Members", None)
                ),
            }
            return render(request, "launch/project_members.html", context=context)

        membership = form.save(project.pk, request.user)
        messages.success(request, "User has been added to project.")
        return HttpResponseRedirect(
            reverse("project_members", args=[project.pk])
        )


@login_required
def membership_update(request, pk):
    membership = get_object_or_404(ProjectMembership.objects.select_related("user", "project"), id=pk)

    if request.method == "GET":
        context = {
            "membership": membership,
            "form": ProjectMembershipUpdateForm(instance=membership)
        }

        return render(request, "launch/membership_update.html", context=context)

    if request.method == "POST":
        form = ProjectMembershipUpdateForm(request.POST, request.FILES, instance=membership)

        if not form.is_valid():
            context = {
                "membership": membership,
                "form": form,
            }
            return render(request, "launch/membership_update.html", context=context)

        membership = form.save()
        messages.success(request, "Membership has been updated.")
        return HttpResponseRedirect(
            reverse("membership_update", args=[membership.pk])
        )


@login_required
def membership_delete(request, pk):
    membership = get_object_or_404(ProjectMembership.objects.select_related("user", "project"), id=pk)

    if request.method == "GET":
        context = {
            "membership": membership,
        }

        return render(request, "launch/membership_delete.html", context=context)

    if request.method == "POST":
        project_id = membership.project_id

        membership.delete()
        messages.success(request, "Membership has been deleted.")
        return HttpResponseRedirect(
            reverse("project_members", args=[project_id])
        )


@login_required
def action_list(request, pk):
    actions_prefetch = Prefetch("actions", Action.objects.prefetch_related("comments").order_by("due_date"))

    project = get_object_or_404(Project.objects.prefetch_related(
        actions_prefetch
    ), pk=pk)

    all_actions = list(project.actions.all())

    todays_actions = [a for a in all_actions if a.due_date == now().date()]
    upcoming_actions = [a for a in all_actions if a.due_date > now().date()]
    other_actions = [a for a in all_actions if a.due_date < now().date()]

    context = {
        "project": project,
        "actions": project.actions.all(),
        "todays_actions": todays_actions,
        "upcoming_actions": upcoming_actions,
        "other_actions": other_actions,
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
                "due_date": now().date(),
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
def action_update(request, pk):

    if request.method == "GET":

        action = get_object_or_404(Action.objects.select_related('project'), id=pk)

        context = {
            "form": ActionUpdateForm(instance=action),
            "action": action,
             "breadcrumbs": (
                ("Launch", "/"),
                ("Projects", reverse("project_list")),
                (action.project.name, reverse("project_detail", args=[action.project.pk])),
                ("Actions", reverse("action_list", args=[action.project.pk])),
                ("Update", None)
            )
        }

        return render(request, "launch/action_update.html", context=context)

    if request.method == "POST":
        action = get_object_or_404(Action.objects.select_related('project'), id=pk)
        form = ActionUpdateForm(request.POST, request.FILES, instance=action)
        if not form.is_valid():
            context = {
                "form": form,
                "action": action,
                "breadcrumbs": (
                    ("Launch", "/"),
                    ("Projects", reverse("project_list")),
                    (action.project.name, reverse("project_detail", args=[action.project.pk])),
                    ("Actions", reverse("action_list", args=[action.project.pk])),
                    ("Update", None)
                )
            }

            messages.error(request, "Please correct the form errors and resubmit")
            return render(request, "launch/action_update.html", context=context)

        form.save()
        messages.success(request, "Action has been updated.")
        return HttpResponseRedirect(
            reverse("action_list", args=[action.project.pk])
        )

@login_required
def action_detail(request, pk):
    comments_prefetch = Prefetch("comments", Comment.objects.order_by("time_created"))
    action = get_object_or_404(Action.objects.prefetch_related(comments_prefetch), pk=pk)

    context = {
        "action": action,
        "comment_form": CommentCreateForm(
            initial={
                "content_type": ContentType.objects.get_for_model(Action),
                "object_id": action.pk,
            }
        ),
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
    attachment.mime_type = mime_type or ""
    attachment.created_by = request.user
    attachment.save()

    next_url = request.POST.get("next")
    if next_url:
        return HttpResponseRedirect(next_url)

    return HttpResponse("OK")


@login_required()
def risk_list(request, pk):
    project = get_object_or_404(Project.objects.prefetch_related("risks"), pk=pk)

    context = {
        "project": project,
        "breadcrumbs": (
            ("Launch", "/"),
            ("Projects", reverse("project_list")),
            (project.name, reverse("project_detail", args=[project.pk])),
            ("Risks", None)
        )
    }

    return render(request, "launch/risk_list.html", context=context)


@login_required()
def issue_list(request, pk):
    issues_prefetch = Prefetch("issues", Issue.objects.select_related("created_by"))

    project = get_object_or_404(Project.objects.prefetch_related(issues_prefetch), pk=pk)

    context = {
        "project": project,
        "breadcrumbs": (
            ("Launch", "/"),
            ("Projects", reverse("project_list")),
            (project.name, reverse("project_detail", args=[project.pk])),
            ("Issues", None)
        )
    }

    return render(request, "launch/issue_list.html", context=context)


@login_required()
def decision_list(request, pk):
    decisions_prefetch = Prefetch("decisions", Decision.objects.select_related("created_by"))

    project = get_object_or_404(Project.objects.prefetch_related(decisions_prefetch), pk=pk)

    context = {
        "project": project,
        "breadcrumbs": (
            ("Launch", "/"),
            ("Projects", reverse("project_list")),
            (project.name, reverse("project_detail", args=[project.pk])),
            ("Decisions", None)
        )
    }

    return render(request, "launch/decision_list.html", context=context)


@login_required()
def gap_list(request, pk):
    gaps_prefetch = Prefetch("gaps", Gap.objects.select_related("created_by"))
    project = get_object_or_404(Project.objects.prefetch_related(gaps_prefetch), pk=pk)

    context = {
        "project": project,
        "breadcrumbs": (
            ("Launch", "/"),
            ("Projects", reverse("project_list")),
            (project.name, reverse("project_detail", args=[project.pk])),
            ("Gaps", None)
        )
    }

    return render(request, "launch/gap_list.html", context=context)


@login_required()
def risk_create(request, pk):
    project = get_object_or_404(Project.objects.all(), pk=pk)

    context = {}

    if request.method == "GET":
        context["form"] = RiskCreateForm(
            initial={
                "name": words(count=6, common=False),
                "description": "\n\n".join(paragraphs(count=4, common=False)),
            }
        )
        return render(request, "launch/create.html", context=context)

    if request.method == "POST":
        form = RiskCreateForm(request.POST, request.FILES)

        if not form.is_valid():
            context["form"] = form
            return render(request, "launch/create.html", context=context)

        obj = form.save(commit=False)
        obj.created_by = request.user
        obj.project = project
        obj.save()

        messages.success(request, "Risk has been created.")
        return HttpResponseRedirect(
            reverse("risk_list", args=[project.pk])
        )


@login_required()
def issue_create(request, pk):
    project = get_object_or_404(Project.objects.all(), pk=pk)

    context = {}

    if request.method == "GET":
        context["form"] = IssueCreateForm(
            initial={
                "name": words(count=6, common=False),
                "description": "\n\n".join(paragraphs(count=4, common=False)),
            }
        )
        return render(request, "launch/create.html", context=context)

    if request.method == "POST":
        form = IssueCreateForm(request.POST, request.FILES)

        if not form.is_valid():
            context["form"] = form
            return render(request, "launch/create.html", context=context)

        obj = form.save(commit=False)
        obj.created_by = request.user
        obj.project = project
        obj.save()

        messages.success(request, "Issue has been created.")
        return HttpResponseRedirect(
            reverse("issue_list", args=[project.pk])
        )


@login_required()
def decision_create(request, pk):
    project = get_object_or_404(Project.objects.all(), pk=pk)

    context = {}

    if request.method == "GET":
        context["form"] = DecisionCreateForm(
            initial={
                "name": words(count=6, common=False),
                "description": "\n\n".join(paragraphs(count=4, common=False)),
            }
        )
        return render(request, "launch/create.html", context=context)

    if request.method == "POST":
        form = DecisionCreateForm(request.POST, request.FILES)

        if not form.is_valid():
            context["form"] = form
            return render(request, "launch/create.html", context=context)

        obj = form.save(commit=False)
        obj.created_by = request.user
        obj.project = project
        obj.save()

        messages.success(request, "Decision has been created.")
        return HttpResponseRedirect(
            reverse("decision_list", args=[project.pk])
        )


@login_required()
def gap_create(request, pk):
    project = get_object_or_404(Project.objects.all(), pk=pk)

    context = {}

    if request.method == "GET":
        context["form"] = GapCreateForm(
            initial={
                "name": words(count=6, common=False),
                "description": "\n\n".join(paragraphs(count=4, common=False)),
            }
        )
        return render(request, "launch/create.html", context=context)

    if request.method == "POST":
        form = GapCreateForm(request.POST, request.FILES)

        if not form.is_valid():
            context["form"] = form
            return render(request, "launch/create.html", context=context)

        obj = form.save(commit=False)
        obj.created_by = request.user
        obj.project = project
        obj.save()

        messages.success(request, "Gap has been created.")
        return HttpResponseRedirect(
            reverse("gap_list", args=[project.pk])
        )
