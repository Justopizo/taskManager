"""Forms used by template views."""

from __future__ import annotations

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model

from .models import Comment, Task, Team

User = get_user_model()


class RegisterForm(UserCreationForm):
    """User registration form."""

    email = forms.EmailField()

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email", "bio", "profile_picture")


class LoginForm(AuthenticationForm):
    """Styled authentication form."""


class TeamForm(forms.ModelForm):
    """Create or update a team."""

    class Meta:
        model = Team
        fields = ("name", "description")


class JoinTeamForm(forms.Form):
    """Join a team with its invite code."""

    invite_code = forms.CharField(max_length=12)


class TaskForm(forms.ModelForm):
    """Task create and update form."""

    deadline = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        input_formats=["%Y-%m-%dT%H:%M"],
    )

    class Meta:
        model = Task
        fields = ("title", "description", "status", "priority", "deadline", "assigned_to", "team")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        memberships = user.team_memberships.select_related("team")
        team_ids = [membership.team_id for membership in memberships]
        self.fields["team"].queryset = Team.objects.filter(id__in=team_ids)
        self.fields["assigned_to"].queryset = User.objects.filter(team_memberships__team_id__in=team_ids).distinct()


class CommentForm(forms.ModelForm):
    """Comment form shown on task detail page."""

    class Meta:
        model = Comment
        fields = ("content",)
        widgets = {
            "content": forms.Textarea(attrs={"rows": 3, "placeholder": "Add a comment"}),
        }


class ProfileForm(forms.ModelForm):
    """User profile update form."""

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "bio", "profile_picture")
