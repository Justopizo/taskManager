"""API views for the task manager."""

from __future__ import annotations

from django.contrib.auth import login, logout
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Comment, Notification, Task, Team, TeamMember
from .serializers import (
    CommentSerializer,
    LoginSerializer,
    NotificationSerializer,
    RegisterSerializer,
    TaskSerializer,
    TeamSerializer,
)


class RegisterAPIView(generics.CreateAPIView):
    """Register a new user."""

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LoginAPIView(APIView):
    """Log users in with session authentication."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Authenticate and log the user in."""
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        login(request, serializer.validated_data["user"])
        return Response({"detail": "Logged in successfully."})


class LogoutAPIView(APIView):
    """Log the current user out."""

    def post(self, request):
        """End the current session."""
        logout(request)
        return Response({"detail": "Logged out successfully."})


class TeamViewSet(viewsets.ModelViewSet):
    """CRUD for teams owned or joined by the current user."""

    serializer_class = TeamSerializer

    def get_queryset(self):
        """Restrict teams to the user's memberships."""
        return Team.objects.filter(memberships__user=self.request.user).distinct().select_related("created_by")

    def perform_create(self, serializer):
        """Create the team and add the creator as admin."""
        team = serializer.save(created_by=self.request.user)
        TeamMember.objects.create(team=team, user=self.request.user, role=TeamMember.ROLE_ADMIN)

    @action(detail=True, methods=["post"], url_path="join")
    def join(self, request, pk=None):
        """Join an existing team with an invite code."""
        team = get_object_or_404(Team, pk=pk)
        invite_code = request.data.get("invite_code", "").strip().upper()
        if invite_code != team.invite_code:
            return Response({"detail": "Invalid invite code."}, status=status.HTTP_400_BAD_REQUEST)
        TeamMember.objects.get_or_create(team=team, user=request.user, defaults={"role": TeamMember.ROLE_MEMBER})
        return Response({"detail": "Joined team successfully."})


class TaskViewSet(viewsets.ModelViewSet):
    """CRUD for tasks with filtering support."""

    serializer_class = TaskSerializer

    def get_queryset(self):
        """Filter tasks by the current user's teams and query params."""
        queryset = (
            Task.objects.filter(team__memberships__user=self.request.user)
            .select_related("team", "created_by", "assigned_to")
            .distinct()
        )
        team_id = self.request.query_params.get("team")
        status_value = self.request.query_params.get("status")
        priority = self.request.query_params.get("priority")
        if team_id:
            queryset = queryset.filter(team_id=team_id)
        if status_value:
            queryset = queryset.filter(status=status_value)
        if priority:
            queryset = queryset.filter(priority=priority)
        return queryset

    def perform_create(self, serializer):
        """Create a task as the current user."""
        serializer.save(created_by=self.request.user)


class TaskCommentListCreateAPIView(generics.ListCreateAPIView):
    """List and create comments for a task."""

    serializer_class = CommentSerializer

    def get_queryset(self):
        """Return comments for tasks in the user's teams."""
        return Comment.objects.filter(
            task_id=self.kwargs["pk"],
            task__team__memberships__user=self.request.user,
        ).select_related("author", "task")

    def perform_create(self, serializer):
        """Create a comment for the specified task."""
        task = get_object_or_404(Task, pk=self.kwargs["pk"], team__memberships__user=self.request.user)
        serializer.save(author=self.request.user, task=task)


class NotificationListAPIView(generics.ListAPIView):
    """List notifications for the current user."""

    serializer_class = NotificationSerializer

    def get_queryset(self):
        """Return notifications belonging to the current user."""
        return Notification.objects.filter(user=self.request.user)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats_api(request):
    """Return dashboard statistics for the current user."""
    tasks = Task.objects.filter(team__memberships__user=request.user).distinct()
    status_counts = tasks.values("status").annotate(count=Count("id"))
    upcoming = tasks.filter(deadline__gte=timezone.now()).order_by("deadline")[:5]
    return Response(
        {
            "status_counts": list(status_counts),
            "upcoming_deadlines": TaskSerializer(upcoming, many=True).data,
            "overdue_count": tasks.filter(deadline__lt=timezone.now()).exclude(status=Task.STATUS_DONE).count(),
            "assigned_to_me": tasks.filter(assigned_to=request.user).count(),
            "high_priority_count": tasks.filter(priority__in=[Task.PRIORITY_HIGH, Task.PRIORITY_URGENT]).count(),
        }
    )
