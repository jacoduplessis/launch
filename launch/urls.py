from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from launch import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("dashboard/", views.project_list, name="dashboard_index"),
    path("project-create/", views.project_create, name="project_create"),
    path("projects/", views.project_list, name="project_list"),
    path("projects/<int:pk>/", views.project_detail, name="project_detail"),
    path("projects/<int:pk>/update/", views.project_update, name="project_update"),
    path("projects/<int:pk>/image/", views.project_image, name="project_image"),
    path("projects/<int:pk>/actions/", views.action_list, name="action_list"),
    path("projects/<int:pk>/risks/", views.risk_list, name="risk_list"),
    path("projects/<int:pk>/issues/", views.issue_list, name="issue_list"),
    path("projects/<int:pk>/decisions/", views.decision_list, name="decision_list"),
    path("projects/<int:pk>/gaps/", views.gap_list, name="gap_list"),
    path("projects/<int:pk>/members/", views.project_members, name="project_members"),
    path("projects/<int:pk>/actions/create/", views.action_create, name="action_create"),
    path("projects/<int:pk>/risks/create/", views.risk_create, name="risk_create"),
    path("projects/<int:pk>/issues/create/", views.issue_create, name="issue_create"),
    path("projects/<int:pk>/decisions/create/", views.decision_create, name="decision_create"),
    path("projects/<int:pk>/gaps/create/", views.gap_create, name="gap_create"),
    path("actions/<int:pk>/", views.action_detail, name="action_detail"),
    path("actions/<int:pk>/update/", views.action_update, name="action_update"),
    path("membership/<int:pk>/update/", views.membership_update, name="membership_update"),
    path("membership/<int:pk>/delete/", views.membership_delete, name="membership_delete"),
    path("comment-create/", views.comment_create, name="comment_create"),
    path("attachment-create/", views.attachment_create, name="attachment_create"),
    path("", views.index, name="index"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)