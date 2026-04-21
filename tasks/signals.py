"""Signal handlers for tasks app."""

from __future__ import annotations

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import Notification, Task, TeamMember


@receiver(pre_save, sender=Task)
def track_previous_assignee(sender, instance: Task, **kwargs) -> None:
    """Store previous assignee before save so notifications only fire on change."""
    if not instance.pk:
        instance._previous_assigned_to_id = None
        instance._previous_status = None
        return
    previous = sender.objects.filter(pk=instance.pk).values_list("assigned_to_id", flat=True).first()
    instance._previous_assigned_to_id = previous
    previous_status = sender.objects.filter(pk=instance.pk).values_list("status", flat=True).first()
    instance._previous_status = previous_status


@receiver(post_save, sender=Task)
def create_assignment_notification(sender, instance: Task, created: bool, **kwargs) -> None:
    """Create a notification when a task is assigned to a user."""
    assignee_id = instance.assigned_to_id
    previous_id = getattr(instance, "_previous_assigned_to_id", None)
    if assignee_id and (created or assignee_id != previous_id):
        Notification.objects.create(
            user=instance.assigned_to,
            message=f"You were assigned to task '{instance.title}'.",
            notification_type=Notification.TYPE_TASK_ASSIGNED,
            action=Notification.ACTION_VIEW,
            link=instance.get_absolute_url(),
        )


@receiver(post_save, sender=Task)
def create_status_notification(sender, instance: Task, created: bool, **kwargs) -> None:
    """Create notifications when task status changes to done."""
    if created:
        return
    previous_status = getattr(instance, "_previous_status", None)
    if instance.status == Task.STATUS_DONE and previous_status != Task.STATUS_DONE:
        if instance.created_by and instance.created_by != instance.assigned_to:
            Notification.objects.create(
                user=instance.created_by,
                message=f"Task '{instance.title}' has been completed by {instance.assigned_to.get_full_name() or instance.assigned_to.username}.",
                notification_type=Notification.TYPE_TASK_COMPLETED,
                action=Notification.ACTION_VIEW,
                link=instance.get_absolute_url(),
            )


@receiver(post_save, sender=TeamMember)
def notify_team_member_joined(sender, instance: TeamMember, created: bool, **kwargs) -> None:
    """Create notifications when a member joins a team."""
    if not created:
        return
    team = instance.team
    for member in team.memberships.exclude(user=instance.user).select_related("user"):
        Notification.objects.create(
            user=member.user,
            message=f"{instance.user.get_full_name() or instance.user.username} joined your team '{team.name}'.",
            notification_type=Notification.TYPE_MEMBER_JOINED,
            action=Notification.ACTION_VIEW,
            link=team.get_absolute_url(),
        )
