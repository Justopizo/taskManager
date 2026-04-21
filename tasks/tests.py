"""Basic automated tests for the tasks app."""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Notification, Task, Team, TeamMember
from .views import DashboardView

User = get_user_model()


class TaskModelTests(TestCase):
    """Verify task model behavior."""

    def setUp(self):
        """Create shared test data."""
        self.user = User.objects.create_user(username="alice", email="alice@example.com", password="password123")
        self.team = Team.objects.create(name="Product", created_by=self.user)
        TeamMember.objects.create(team=self.team, user=self.user, role=TeamMember.ROLE_ADMIN)

    def test_task_creation(self):
        """A task can be created and linked to a team."""
        task = Task.objects.create(
            title="Write docs",
            description="Prepare onboarding docs",
            priority=Task.PRIORITY_HIGH,
            deadline=timezone.now() + timedelta(days=1),
            created_by=self.user,
            team=self.team,
        )
        self.assertEqual(task.title, "Write docs")
        self.assertEqual(task.team, self.team)


class TeamMembershipTests(TestCase):
    """Verify team membership behavior."""

    def test_team_membership(self):
        """Users can be attached to a team."""
        owner = User.objects.create_user(username="owner", email="owner@example.com", password="password123")
        teammate = User.objects.create_user(username="teammate", email="mate@example.com", password="password123")
        team = Team.objects.create(name="Engineering", created_by=owner)
        TeamMember.objects.create(team=team, user=owner, role=TeamMember.ROLE_ADMIN)
        membership = TeamMember.objects.create(team=team, user=teammate, role=TeamMember.ROLE_MEMBER)
        self.assertEqual(membership.team, team)
        self.assertEqual(team.memberships.count(), 2)


class NotificationSignalTests(TestCase):
    """Verify task assignment notifications."""

    def setUp(self):
        """Create base test objects."""
        self.creator = User.objects.create_user(username="creator", email="creator@example.com", password="password123")
        self.assignee = User.objects.create_user(username="assignee", email="assignee@example.com", password="password123")
        self.team = Team.objects.create(name="Ops", created_by=self.creator)
        TeamMember.objects.create(team=self.team, user=self.creator, role=TeamMember.ROLE_ADMIN)
        TeamMember.objects.create(team=self.team, user=self.assignee, role=TeamMember.ROLE_MEMBER)

    def test_notification_created_on_task_assignment(self):
        """Assigning a task creates a notification."""
        Task.objects.create(
            title="Ship release",
            created_by=self.creator,
            assigned_to=self.assignee,
            team=self.team,
        )
        self.assertEqual(Notification.objects.filter(user=self.assignee).count(), 1)


class DashboardViewTests(TestCase):
    """Verify the dashboard page renders for authenticated users."""

    def setUp(self):
        """Create a request factory for view-level assertions."""
        self.factory = RequestFactory()

    def test_dashboard_requires_login_and_renders(self):
        """The dashboard redirects anonymous users and loads for authenticated users."""
        user = User.objects.create_user(username="viewer", email="viewer@example.com", password="password123")
        team = Team.objects.create(name="Support", created_by=user)
        TeamMember.objects.create(team=team, user=user, role=TeamMember.ROLE_ADMIN)
        client = Client()
        response = client.get(reverse("tasks:dashboard"))
        self.assertEqual(response.status_code, 302)

        request = self.factory.get(reverse("tasks:dashboard"))
        request.user = user
        response = DashboardView.as_view()(request)
        self.assertEqual(response.status_code, 200)
