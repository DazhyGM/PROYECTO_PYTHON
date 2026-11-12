from django.conf import settings
from django.db import models


class Rol(models.Model):
    """Tabla roles. Catálogo de los dos roles."""

    ADMINISTRADOR = "administrador"
    USUARIO = "usuario"

    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=50)

    class Meta:
        db_table = "roles"
        verbose_name = "rol"
        verbose_name_plural = "roles"

    def __str__(self):
        return "%s" % self.nombre

    @classmethod
    def obtener(cls, codigo):
        nombres = {
            cls.ADMINISTRADOR: "Administrador",
            cls.USUARIO: "Usuario normal",
        }
        rol, _ = cls.objects.get_or_create(codigo=codigo, defaults={"nombre": nombres[codigo]})
        return rol


class Usuario(models.Model):
    """Tabla cuentas_usuario. Una fila por persona."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="usuario")
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT, related_name="usuarios")

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

    def __str__(self):
        return "%s" % self.user.username

    def es_administrador(self):
        return self.rol.codigo == Rol.ADMINISTRADOR


class Servicio(models.Model):
    """Tabla cuentas_servicio. Catálogo compartido."""

    nombre = models.CharField(max_length=200)

    class Meta:
        verbose_name = "servicio"
        verbose_name_plural = "servicios"

    def __str__(self):
        return "%s" % self.nombre


class Cuenta(models.Model):
    """Tabla cuentas_cuenta. Un recibo de una persona."""

    PROPIA = "propia"
    GRUPO = "grupo"
    ALCANCES = [
        (PROPIA, "Cuenta propia"),
        (GRUPO, "Cuenta del grupo"),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    alcance = models.CharField(max_length=10, choices=ALCANCES, default=GRUPO)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    mes = models.CharField(max_length=200)
    valor = models.IntegerField(default=0)
    vence = models.DateTimeField("fecha de vencimiento")
    pagada = models.BooleanField(default=False)

    class Meta:
        verbose_name = "cuenta"
        verbose_name_plural = "cuentas"

    def __str__(self):
        return "%s %s" % (self.servicio, self.mes)
