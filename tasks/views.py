"""Template-based views for the collaborative task manager."""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView,
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView

from .forms import CommentForm, JoinTeamForm, LoginForm, ProfileForm, RegisterForm, TaskForm, TeamForm
from .models import Comment, Notification, Task, Team, TeamMember


class UserLoginView(LoginView):
    """Session-based login view."""

    template_name = "registration/login.html"
    authentication_form = LoginForm


class UserRegisterView(CreateView):
    """User registration page."""

    form_class = RegisterForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("tasks:dashboard")

    def form_valid(self, form):
        """Log the new user in after registration."""
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class UserPasswordResetView(PasswordResetView):
    """Password reset view using console email backend."""

    template_name = "registration/password_reset_form.html"
    email_template_name = "registration/password_reset_email.txt"
    success_url = reverse_lazy("tasks:password_reset_done")


class UserPasswordResetDoneView(PasswordResetDoneView):
    """Password reset sent page."""

    template_name = "registration/password_reset_done.html"


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    """Password reset confirmation view."""

    template_name = "registration/password_reset_confirm.html"
    success_url = reverse_lazy("tasks:password_reset_complete")


class UserPasswordResetCompleteView(PasswordResetCompleteView):
    """Password reset completion view."""

    template_name = "registration/password_reset_complete.html"


class DashboardView(LoginRequiredMixin, TemplateView):
    """Display a summary dashboard for the current user."""

    template_name = "tasks/dashboard.html"

    def get_context_data(self, **kwargs):
        """Build dashboard statistics and recent activity."""
        context = super().get_context_data(**kwargs)
        tasks = (
            Task.objects.filter(team__memberships__user=self.request.user)
            .select_related("team", "assigned_to")
            .distinct()
        )
        now = timezone.now()
        priority_counts = {
            item["priority"]: item["count"]
            for item in tasks.values("priority").annotate(count=Count("id"))
        }
        context.update(
            {
                "total_tasks": tasks.count(),
                "completed_tasks": tasks.filter(status=Task.STATUS_DONE).count(),
                "pending_tasks": tasks.filter(status=Task.STATUS_PENDING).count(),
                "overdue_tasks": tasks.filter(deadline__lt=now).exclude(status=Task.STATUS_DONE).count(),
                "recent_tasks": tasks.order_by("-updated_at")[:5],
                "priority_counts": priority_counts,
            }
        )
        return context


class TaskListView(LoginRequiredMixin, ListView):
    """Task list with search and filtering."""

    model = Task
    template_name = "tasks/task_list.html"
    context_object_name = "tasks_list"
    paginate_by = 10

    def get_queryset(self):
        """Apply query string filters."""
        queryset = (
            Task.objects.filter(team__memberships__user=self.request.user)
            .select_related("team", "assigned_to", "created_by")
            .distinct()
        )
        search = self.request.GET.get("q", "").strip()
        status_value = self.request.GET.get("status", "").strip()
        priority = self.request.GET.get("priority", "").strip()
        team_id = self.request.GET.get("team", "").strip()
        assigned_to_me = self.request.GET.get("assigned_to_me", "").strip()
        if search:
            queryset = queryset.filter(title__icontains=search)
        if status_value:
            queryset = queryset.filter(status=status_value)
        if priority:
            queryset = queryset.filter(priority=priority)
        if team_id:
            queryset = queryset.filter(team_id=team_id)
        if assigned_to_me:
            queryset = queryset.filter(assigned_to=self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        """Expose filter metadata to the template."""
        context = super().get_context_data(**kwargs)
        context["teams"] = Team.objects.filter(memberships__user=self.request.user).distinct()
        context["status_choices"] = Task.STATUS_CHOICES
        context["priority_choices"] = Task.PRIORITY_CHOICES
        context["pending_count"] = self.object_list.filter(status=Task.STATUS_PENDING).count()
        context["in_progress_count"] = self.object_list.filter(status=Task.STATUS_IN_PROGRESS).count()
        context["done_count"] = self.object_list.filter(status=Task.STATUS_DONE).count()
        return context


class TaskCreateView(LoginRequiredMixin, CreateView):
    """Create new tasks."""

    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"

    def get_form_kwargs(self):
        """Pass the current user to the form for queryset scoping."""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Set creator and persist the task."""
        form.instance.created_by = self.request.user
        messages.success(self.request, "Task created successfully.")
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    """Edit an existing task."""

    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"

    def get_queryset(self):
        """Limit edits to tasks in the user's teams."""
        return Task.objects.filter(team__memberships__user=self.request.user).distinct()

    def get_form_kwargs(self):
        """Pass the current user to the form."""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Show a success flash."""
        messages.success(self.request, "Task updated successfully.")
        return super().form_valid(form)


class TaskDetailView(LoginRequiredMixin, DetailView):
    """Task detail page with comments."""

    model = Task
    template_name = "tasks/task_detail.html"
    context_object_name = "task"

    def get_queryset(self):
        """Limit access to tasks in the user's teams."""
        return Task.objects.filter(team__memberships__user=self.request.user).select_related(
            "team", "created_by", "assigned_to"
        ).distinct()

    def get_context_data(self, **kwargs):
        """Add comments, assignment options, and permissions."""
        context = super().get_context_data(**kwargs)
        task = self.object
        context["comment_form"] = CommentForm()
        context["team_members"] = task.team.memberships.select_related("user")
        context["can_edit"] = task.created_by == self.request.user
        context["comments_count"] = task.comments.count()
        return context


@login_required
def task_comments_partial(request, pk):
    """Render comments markup for periodic refresh."""
    task = get_object_or_404(Task, pk=pk, team__memberships__user=request.user)
    return render(request, "tasks/partials/comments_list.html", {"task": task})


@login_required
def add_comment(request, pk):
    """Add a comment to a task."""
    task = get_object_or_404(Task, pk=pk, team__memberships__user=request.user)
    form = CommentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        comment = form.save(commit=False)
        comment.task = task
        comment.author = request.user
        comment.save()
        messages.success(request, "Comment added.")
    return redirect(task.get_absolute_url())


@login_required
def assign_task(request, pk):
    """Assign a task to a team member."""
    task = get_object_or_404(Task, pk=pk, team__memberships__user=request.user)
    user_id = request.POST.get("assigned_to")
    membership = get_object_or_404(TeamMember, team=task.team, user_id=user_id)
    task.assigned_to = membership.user
    task.save()
    messages.success(request, "Task assigned successfully.")
    return redirect(task.get_absolute_url())


@login_required
def change_task_status(request, pk):
    """Change task status - only team members can mark tasks as done/pending."""
    task = get_object_or_404(Task, pk=pk, team__memberships__user=request.user)
    is_team_member = TeamMember.objects.filter(team=task.team, user=request.user).exists()
    new_status = request.POST.get("status")
    
    if not is_team_member:
        messages.error(request, "Only team members can change task status.")
        return redirect(task.get_absolute_url())
    
    if new_status in dict(Task.STATUS_CHOICES):
        old_status = task.status
        task.status = new_status
        task.save(update_fields=["status"])
        
        if new_status == Task.STATUS_DONE and old_status != Task.STATUS_DONE:
            messages.success(request, f"Task marked as done. It has been moved to completed tasks.")
        else:
            messages.success(request, f"Task marked as {task.get_status_display()}.")
    return redirect(task.get_absolute_url())


class TeamListView(LoginRequiredMixin, ListView):
    """Display teams for the current user."""

    model = Team
    template_name = "tasks/team_list.html"
    context_object_name = "teams"

    def get_queryset(self):
        """Restrict teams to the user's memberships."""
        return Team.objects.filter(memberships__user=self.request.user).distinct()

    def get_context_data(self, **kwargs):
        """Include the join form."""
        context = super().get_context_data(**kwargs)
        context["join_form"] = JoinTeamForm()
        return context


class TeamCreateView(LoginRequiredMixin, CreateView):
    """Create a new team."""

    model = Team
    form_class = TeamForm
    template_name = "tasks/team_form.html"

    def form_valid(self, form):
        """Add the creator as an admin after creation."""
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        TeamMember.objects.create(team=self.object, user=self.request.user, role=TeamMember.ROLE_ADMIN)
        messages.success(self.request, "Team created successfully.")
        return response


class TeamDetailView(LoginRequiredMixin, DetailView):
    """Show a team's members and tasks."""

    model = Team
    template_name = "tasks/team_detail.html"
    context_object_name = "team"

    def get_queryset(self):
        """Restrict access to the user's teams."""
        return Team.objects.filter(memberships__user=self.request.user).prefetch_related("memberships__user", "tasks")


@login_required
def join_team(request):
    """Join a team using its invite code."""
    form = JoinTeamForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        invite_code = form.cleaned_data["invite_code"].strip().upper()
        team = get_object_or_404(Team, invite_code=invite_code)
        TeamMember.objects.get_or_create(team=team, user=request.user, defaults={"role": TeamMember.ROLE_MEMBER})
        messages.success(request, f"You joined {team.name}.")
    return redirect("tasks:team_list")


class NotificationListView(LoginRequiredMixin, ListView):
    """Display notifications for the current user."""

    model = Notification
    template_name = "tasks/notifications.html"
    context_object_name = "notifications"

    def get_queryset(self):
        """Return the current user's notifications."""
        return Notification.objects.filter(user=self.request.user)


@login_required
def mark_notification_read(request, pk):
    """Mark one notification as read."""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save(update_fields=["is_read"])
    return redirect("tasks:notifications")


@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read."""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, "All notifications marked as read.")
    return redirect("tasks:notifications")


class ProfileView(LoginRequiredMixin, UpdateView):
    """Update the current user's profile."""

    form_class = ProfileForm
    template_name = "tasks/profile.html"
    success_url = reverse_lazy("tasks:profile")

    def get_object(self, queryset=None):
        """Return the current user."""
        return self.request.user

    def get_context_data(self, **kwargs):
        """Add assigned tasks to the profile page."""
        context = super().get_context_data(**kwargs)
        context["assigned_tasks"] = self.request.user.assigned_tasks.select_related("team").order_by("deadline")
        return context

    def form_valid(self, form):
        """Show a flash message on success."""
        messages.success(self.request, "Profile updated successfully.")
        return super().form_valid(form)


class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """Password change page for authenticated users."""

    template_name = "registration/password_change_form.html"
    success_url = reverse_lazy("tasks:profile")

    def form_valid(self, form):
        """Show a success message after changing password."""
        messages.success(self.request, "Password changed successfully.")
        return super().form_valid(form)


@login_required
def notifications_dropdown(request):
    """Return recent notifications for dynamic refresh if needed later."""
    payload = list(
        Notification.objects.filter(user=request.user).values("message", "is_read", "created_at", "link")[:5]
    )
    return JsonResponse({"notifications": payload})
