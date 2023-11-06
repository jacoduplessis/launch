from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.contrib.auth.views import LoginView as BaseLoginView, LogoutView as BaseLogoutView
from django.urls import reverse
from django.contrib import messages

from launch.forms import ProjectCreateForm
from launch.models import Project, OrganisationMembership, Action


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
        "projects": Project.objects.filter(created_by_id=request.user.id)
    }
    return render(request, template_name="launch/dashboard_index.html", context=context)


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
        context["form"] = ProjectCreateForm()
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

    project = get_object_or_404(Project, pk=pk)
    context = {
        "project": project,
        "breadcrumbs": (
            ("Launch", "/"),
            ("Projects", reverse("project_list")),
            ("Detail", None)
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