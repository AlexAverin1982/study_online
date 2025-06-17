from django.contrib import admin
from django.contrib.auth.models import Group
from .models import CustomUser

from groupadmin_users.forms import GroupAdminForm


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "is_superuser", "is_staff", "email")

    search_fields = (
        "username",
        "email",
    )


# Unregister the original Group admin.
admin.site.unregister(Group)


# Create a new Group admin.
class GroupAdmin(admin.ModelAdmin):
    # Use our custom form.
    form = GroupAdminForm
    # Filter permissions horizontal as well.
    filter_horizontal = ['permissions']


# Register the new Group ModelAdmin.
admin.site.register(Group, GroupAdmin)
