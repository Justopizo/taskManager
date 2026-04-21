"""URL routes for template and API views."""

from django.contrib.auth.views import LogoutView
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import api_views, views

app_name = "tasks"

router = DefaultRouter()
router.register("teams", api_views.TeamViewSet, basename="api-teams")
router.register("tasks", api_views.TaskViewSet, basename="api-tasks")

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", views.UserRegisterView.as_view(), name="register"),
    path("password-reset/", views.UserPasswordResetView.as_view(), name="password_reset"),
    path("password-reset/done/", views.UserPasswordResetDoneView.as_view(), name="password_reset_done"),
    path(
        "reset/<uidb64>/<token>/",
        views.UserPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("reset/done/", views.UserPasswordResetCompleteView.as_view(), name="password_reset_complete"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile/password/", views.UserPasswordChangeView.as_view(), name="password_change"),
    path("tasks/", views.TaskListView.as_view(), name="task_list"),
    path("tasks/create/", views.TaskCreateView.as_view(), name="task_create"),
    path("tasks/<int:pk>/", views.TaskDetailView.as_view(), name="task_detail"),
    path("tasks/<int:pk>/edit/", views.TaskUpdateView.as_view(), name="task_edit"),
    path("tasks/<int:pk>/comments/", views.add_comment, name="add_comment"),
    path("tasks/<int:pk>/comments/partial/", views.task_comments_partial, name="task_comments_partial"),
    path("tasks/<int:pk>/assign/", views.assign_task, name="assign_task"),
    path("tasks/<int:pk>/status/", views.change_task_status, name="change_task_status"),
    path("teams/", views.TeamListView.as_view(), name="team_list"),
    path("teams/create/", views.TeamCreateView.as_view(), name="team_create"),
    path("teams/join/", views.join_team, name="join_team"),
    path("teams/<int:pk>/", views.TeamDetailView.as_view(), name="team_detail"),
    path("notifications/", views.NotificationListView.as_view(), name="notifications"),
    path("notifications/<int:pk>/read/", views.mark_notification_read, name="mark_notification_read"),
    path("notifications/read-all/", views.mark_all_notifications_read, name="mark_all_notifications_read"),
    path("notifications/dropdown/", views.notifications_dropdown, name="notifications_dropdown"),
    path("api/register/", api_views.RegisterAPIView.as_view(), name="api_register"),
    path("api/login/", api_views.LoginAPIView.as_view(), name="api_login"),
    path("api/logout/", api_views.LogoutAPIView.as_view(), name="api_logout"),
    path("api/tasks/<int:pk>/comments/", api_views.TaskCommentListCreateAPIView.as_view(), name="api_task_comments"),
    path("api/notifications/", api_views.NotificationListAPIView.as_view(), name="api_notifications"),
    path("api/dashboard/stats/", api_views.dashboard_stats_api, name="api_dashboard_stats"),
    path("api/", include(router.urls)),
]
