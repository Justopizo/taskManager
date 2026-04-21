"""URL routing for the project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path, re_path
from django.views.generic import TemplateView

from tasks.views import UserLoginView, UserRegisterView


def root_redirect(request):
    """Send unauthenticated users to /landing/ and authenticated users to /dashboard/."""
    if request.user.is_authenticated:
        return redirect("/dashboard/")
    return redirect("/landing/")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("landing/", TemplateView.as_view(template_name="landing.html"), name="landing"),
    path("accounts/login/", UserLoginView.as_view(), name="account_login"),
    path("accounts/register/", UserRegisterView.as_view(), name="account_register"),
    path("dashboard/", include("tasks.urls")),
    re_path(r"^$", root_redirect, name="root"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
