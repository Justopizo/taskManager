"""Database models for the collaborative task manager."""

from __future__ import annotations

import secrets
import string

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    """Custom user model with profile metadata."""

    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    profile_picture = models.URLField(blank=True)

    def __str__(self) -> str:
        """Return the user's display label."""
        return self.get_full_name() or self.username


class Team(models.Model):
    """A collaborative team that owns tasks."""

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_teams",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    invite_code = models.CharField(max_length=12, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        """Return the team name."""
        return self.name

    def save(self, *args, **kwargs) -> None:
        """Create a unique invite code automatically when needed."""
        if not self.invite_code:
            alphabet = string.ascii_uppercase + string.digits
            while True:
                code = "".join(secrets.choice(alphabet) for _ in range(8))
                if not Team.objects.filter(invite_code=code).exists():
                    self.invite_code = code
                    break
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """Return the team detail URL."""
        return reverse("tasks:team_detail", args=[self.pk])


class TeamMember(models.Model):
    """Membership record linking users to teams."""

    ROLE_ADMIN = "admin"
    ROLE_MEMBER = "member"
    ROLE_CHOICES = [
        (ROLE_ADMIN, "Admin"),
        (ROLE_MEMBER, "Member"),
    ]

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="team_memberships",
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_MEMBER)

    class Meta:
        unique_together = ("team", "user")
        ordering = ["team", "user__username"]

    def __str__(self) -> str:
        """Return membership summary."""
        return f"{self.user} in {self.team}"


class Task(models.Model):
    """A task within a team."""

    STATUS_PENDING = "pending"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_DONE = "done"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_DONE, "Done"),
    ]

    PRIORITY_LOW = "low"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_HIGH = "high"
    PRIORITY_URGENT = "urgent"
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, "Low"),
        (PRIORITY_MEDIUM, "Medium"),
        (PRIORITY_HIGH, "High"),
        (PRIORITY_URGENT, "Urgent"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    deadline = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_tasks",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="tasks")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["deadline", "-updated_at"]

    def __str__(self) -> str:
        """Return the task title."""
        return self.title

    def get_absolute_url(self) -> str:
        """Return the task detail URL."""
        return reverse("tasks:task_detail", args=[self.pk])


class Comment(models.Model):
    """Comment attached to a task."""

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        """Return a short comment label."""
        return f"Comment by {self.author} on {self.task}"


class Notification(models.Model):
    """Simple user notification model."""

    TYPE_TASK_ASSIGNED = "task_assigned"
    TYPE_TASK_COMPLETED = "task_completed"
    TYPE_TASK_UPDATED = "task_updated"
    TYPE_MEMBER_JOINED = "member_joined"
    TYPE_MEMBER_REMOVED = "member_removed"
    TYPE_TEAM_INVITE = "team_invite"
    TYPE_CHOICES = [
        (TYPE_TASK_ASSIGNED, "Task Assigned"),
        (TYPE_TASK_COMPLETED, "Task Completed"),
        (TYPE_TASK_UPDATED, "Task Updated"),
        (TYPE_MEMBER_JOINED, "Member Joined"),
        (TYPE_MEMBER_REMOVED, "Member Removed"),
        (TYPE_TEAM_INVITE, "Team Invite"),
    ]

    ACTION_VIEW = "view"
    ACTION_EDIT = "edit"
    ACTION_ASSIGN = "assign"
    ACTION_REPLY = "reply"
    ACTION_ACCEPT = "accept"
    ACTION_JOIN = "join"
    ACTION_NONE = "none"
    ACTION_CHOICES = [
        (ACTION_VIEW, "View Task"),
        (ACTION_EDIT, "Edit Task"),
        (ACTION_ASSIGN, "Assign Task"),
        (ACTION_REPLY, "Reply"),
        (ACTION_ACCEPT, "Accept"),
        (ACTION_JOIN, "Join Team"),
        (ACTION_NONE, "None"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    message = models.CharField(max_length=255)
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_TASK_ASSIGNED)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, default=ACTION_VIEW)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """Return a readable notification label."""
        return f"Notification for {self.user}: {self.message}"
