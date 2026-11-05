from django.contrib import admin

from .models import Cuenta, Servicio


admin.site.register(Servicio)


@admin.register(Cuenta)
class CuentaAdmin(admin.ModelAdmin):
    list_display = ("servicio", "mes", "valor", "vence", "pagada")
    list_filter = ("pagada", "servicio")
