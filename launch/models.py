from django.db import models
from django.conf import settings


class Organisation(models.Model):
    name = models.CharField(max_length=200)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="+")
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Membership', through_fields=('organisation', 'user'))

    def __str__(self):
        return self.name


class OrganisationMembership(models.Model):
    ADMIN = 'admin'
    LEADER = 'leader'
    MEMBER = 'member'

    ROLE_CHOICES = (
        (ADMIN, "Admin"),
        (LEADER, "Leader"),
        (MEMBER, "Member"),
    )

    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+")
    role = models.CharField(max_length=100, choices=ROLE_CHOICES, default=MEMBER)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class ProjectMembership(models.Model):
    ADMIN = 'admin'
    LEADER = 'leader'
    MEMBER = 'member'

    ROLE_CHOICES = (
        (ADMIN, "Admin"),
        (LEADER, "Leader"),
        (MEMBER, "Member"),
    )

    project = models.ForeignKey("Project", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+")
    role = models.CharField(max_length=100, choices=ROLE_CHOICES, default=MEMBER)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class Project(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name="projects")
    name = models.CharField(max_length=100)
    overview = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    sponsor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    lead = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through=ProjectMembership, through_fields=("project", "user"))


class Attachment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    file = models.FileField(upload_to="attachments/", blank=True)
    mime_type = models.CharField(max_length=100)
    size = models.PositiveBigIntegerField(default=0)
