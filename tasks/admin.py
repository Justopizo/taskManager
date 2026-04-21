"""Admin registration for app models."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Comment, Notification, Task, Team, TeamMember, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Admin for the custom user model."""

    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Profile", {"fields": ("bio", "profile_picture")}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ("Profile", {"fields": ("email", "bio", "profile_picture")}),
    )
    list_display = ("username", "email", "is_staff")


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """Admin configuration for teams."""

    list_display = ("name", "created_by", "invite_code", "created_at")
    search_fields = ("name", "invite_code")


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    """Admin configuration for team members."""

    list_display = ("team", "user", "role")
    list_filter = ("role",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin configuration for tasks."""

    list_display = ("title", "team", "status", "priority", "assigned_to", "deadline")
    list_filter = ("status", "priority", "team")
    search_fields = ("title", "description")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin configuration for comments."""

    list_display = ("task", "author", "created_at")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin configuration for notifications."""

    list_display = ("user", "message", "is_read", "created_at")
    list_filter = ("is_read",)
