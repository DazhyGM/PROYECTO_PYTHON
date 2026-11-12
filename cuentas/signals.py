from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Rol, Usuario


@receiver(post_save, sender=get_user_model())
def crear_usuario_del_modelo(sender, instance, created, **kwargs):
    if created:
        codigo = Rol.ADMINISTRADOR if instance.is_staff or instance.is_superuser else Rol.USUARIO
        Usuario.objects.get_or_create(user=instance, defaults={"rol": Rol.obtener(codigo)})
