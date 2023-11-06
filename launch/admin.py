from django.contrib import admin
from .models import Organisation, Project
from django.contrib.auth.models import Group

admin.site.site_header = "Launch Admin"
admin.site.site_title = "Launch Admin"
admin.site.index_title = "Administration"

admin.site.unregister(Group)

@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = [
        "name",
    ]
