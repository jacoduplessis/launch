from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.contrib.auth.views import LoginView as BaseLoginView, LogoutView as BaseLogoutView
from django.urls import reverse


class LoginView(BaseLoginView):
    template_name = "launch/login.html"
    redirect_authenticated_user = True


@login_required
def dashboard_index(request):
    return render(request, template_name="launch/dashboard_index.html")


def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("dashboard_index"))
    return HttpResponseRedirect(reverse("login"))


@login_required()
def project_create(request):
    return render(request, template_name="launch/project_create.html")