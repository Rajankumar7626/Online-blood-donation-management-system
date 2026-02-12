from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("accounts/", include("accounts.urls")),
    path("donors/", include(("donors.urls", "donors"), namespace="donors")),
    path("hospital/", include(("hospitals.urls", "hospital"), namespace="hospital")),
    path("requests/", include(("blood_requests.urls", "requests"), namespace="requests")),
]
