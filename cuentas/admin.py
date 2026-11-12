from django.contrib import admin

from .models import Cuenta, Rol, Servicio, Usuario


admin.site.register(Servicio)


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ("id", "codigo", "nombre")


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("user", "rol")
    list_filter = ("rol",)


@admin.register(Cuenta)
class CuentaAdmin(admin.ModelAdmin):
    list_display = ("usuario", "servicio", "mes", "valor", "vence", "pagada", "alcance")
    list_filter = ("pagada", "alcance", "servicio", "usuario")
