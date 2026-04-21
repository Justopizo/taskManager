"""Serializers for DRF endpoints."""

from __future__ import annotations

from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

from .models import Comment, Notification, Task, Team, TeamMember

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serialize public user fields."""

    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "email", "bio", "profile_picture")


class RegisterSerializer(serializers.ModelSerializer):
    """Create users through the API."""

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "email", "bio", "profile_picture", "password")

    def create(self, validated_data):
        """Create a new user with a hashed password."""
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """Validate login credentials."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Authenticate the user."""
        request = self.context.get("request")
        user = authenticate(request=request, username=attrs["username"], password=attrs["password"])
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        attrs["user"] = user
        return attrs


class TeamMemberSerializer(serializers.ModelSerializer):
    """Serialize team members."""

    user = UserSerializer(read_only=True)

    class Meta:
        model = TeamMember
        fields = ("id", "user", "role")


class TeamSerializer(serializers.ModelSerializer):
    """Serialize teams with member data."""

    created_by = UserSerializer(read_only=True)
    memberships = TeamMemberSerializer(many=True, read_only=True)

    class Meta:
        model = Team
        fields = ("id", "name", "description", "created_by", "created_at", "invite_code", "memberships")
        read_only_fields = ("created_by", "created_at", "invite_code")


class CommentSerializer(serializers.ModelSerializer):
    """Serialize task comments."""

    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "task", "author", "content", "created_at")
        read_only_fields = ("author", "created_at", "task")


class TaskSerializer(serializers.ModelSerializer):
    """Serialize tasks."""

    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="assigned_to",
        write_only=True,
        required=False,
        allow_null=True,
    )
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "description",
            "status",
            "priority",
            "deadline",
            "created_by",
            "assigned_to",
            "assigned_to_id",
            "team",
            "created_at",
            "updated_at",
            "comments",
        )
        read_only_fields = ("created_by", "created_at", "updated_at")

    def validate(self, attrs):
        """Ensure task team membership and assignment are consistent."""
        request = self.context.get("request")
        team = attrs.get("team") or getattr(self.instance, "team", None)
        assigned_to = attrs.get("assigned_to", getattr(self.instance, "assigned_to", None))
        if request and team and not TeamMember.objects.filter(team=team, user=request.user).exists():
            raise serializers.ValidationError("You must belong to the selected team.")
        if team and assigned_to and not TeamMember.objects.filter(team=team, user=assigned_to).exists():
            raise serializers.ValidationError("Assigned user must be a member of the selected team.")
        return attrs


class NotificationSerializer(serializers.ModelSerializer):
    """Serialize notifications."""

    class Meta:
        model = Notification
        fields = ("id", "message", "is_read", "created_at", "link")
