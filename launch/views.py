from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
from django.contrib.auth.views import LoginView as BaseLoginView, LogoutView as BaseLogoutView


class LoginView(BaseLoginView):
    template_name = "launch/login.html"
    redirect_authenticated_user = True


@login_required
def dashboard_index(request):
    return render(request, template_name="launch/dashboard_index.html")