from pathlib import Path

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey

ONE_TO_FIVE = (
    (1, "1"),
    (2, "2"),
    (3, "3"),
    (4, "4"),
    (5, "5"),
)


class OrganisationMembership(models.Model):
    ADMIN = 'admin'
    LEADER = 'leader'
    MEMBER = 'member'

    ROLE_CHOICES = (
        (ADMIN, "Admin"),
        (LEADER, "Leader"),
        (MEMBER, "Member"),
    )

    organisation = models.ForeignKey("Organisation", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+")
    role = models.CharField(max_length=100, choices=ROLE_CHOICES, default=MEMBER)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class Organisation(models.Model):
    name = models.CharField(max_length=200)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="+")
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through=OrganisationMembership, through_fields=('organisation', 'user'))

    def __str__(self):
        return self.name


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
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)


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

    attachments = GenericRelation('Attachment')
    comments = GenericRelation('Comment')

    image = models.ImageField(upload_to="projects/", blank=True)

    def __str__(self):
        return self.name

    def duration_days(self):
        if not (self.start_date and self.end_date):
            return None
        return (self.end_date - self.start_date).days


class Attachment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    file = models.FileField(upload_to="attachments/", blank=True)
    mime_type = models.CharField(max_length=100)
    size = models.PositiveBigIntegerField(default=0)

    @property
    def suffix(self):
        if self.file is None:
            return ""
        return Path(self.file.name).suffix

    @property
    def name(self):
        if self.file is None:
            return ""
        return Path(self.file.name).name


class Comment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    time_created = models.DateTimeField(auto_now_add=True)
    body = models.TextField()


class Action(models.Model):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    PRIORITY_CHOICES = (
        (HIGH, "High"),
        (MEDIUM, "Medium"),
        (LOW, "Low"),
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="actions")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    due_date = models.DateField(null=True)
    priority = models.CharField(max_length=200, choices=PRIORITY_CHOICES, default=MEDIUM)
    sub_tasks = models.TextField(blank=True)
    time_completed = models.DateTimeField(null=True, blank=True)  # tracks completion

    attachments = GenericRelation('Attachment')
    comments = GenericRelation('Comment')

    def __str__(self):
        return f"{self.project_id} {self.name}"


class Risk(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="risks")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    mitigation = models.TextField(blank=True)
    impact = models.PositiveIntegerField(choices=ONE_TO_FIVE)
    likelihood = models.PositiveIntegerField(choices=ONE_TO_FIVE)


class Issue(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="issues")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    impact = models.PositiveIntegerField(choices=ONE_TO_FIVE)


class Decision(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="decisions")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    next_steps = models.TextField(blank=True)


class Gap(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="gaps")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    mitigation = models.TextField(blank=True)
