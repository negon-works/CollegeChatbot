from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("public.urls")),
    path("staff/", include(("staffpanel.urls", "staffpanel"), namespace="staffpanel")),
]
