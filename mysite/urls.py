from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(url="/cuentas/", permanent=False)),
    path("cuentas/", include("cuentas.urls")),
    path("admin/", admin.site.urls),
]
