"""Template context helpers."""

from .models import Notification


def notification_context(request):
    """Expose unread notification metadata to all templates."""
    if not request.user.is_authenticated:
        return {"latest_notifications": [], "unread_notifications_count": 0}

    notifications = Notification.objects.filter(user=request.user).order_by("-created_at")
    return {
        "latest_notifications": notifications[:5],
        "unread_notifications_count": notifications.filter(is_read=False).count(),
    }
