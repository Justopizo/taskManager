"""Custom template filters for task manager."""

from django import template

register = template.Library()


@register.filter
def can_change_status(task, user):
    """Check if user is a team member and can change task status."""
    if not user.is_authenticated:
        return False
    from tasks.models import TeamMember
    return TeamMember.objects.filter(team=task.team, user=user).exists()


@register.filter
def get_status_count(tasks_list, status):
    """Count tasks by status for board columns."""
    return sum(1 for t in tasks_list if t.status == status)