from django.db import migrations, models


def marcar_administradores(apps, schema_editor):
    Usuario = apps.get_model("cuentas", "Usuario")
    for perfil in Usuario.objects.select_related("user"):
        if perfil.user.is_staff or perfil.user.is_superuser:
            perfil.rol = "administrador"
            perfil.save(update_fields=["rol"])


class Migration(migrations.Migration):

    dependencies = [
        ("cuentas", "0002_usuario_y_cuentas"),
    ]

    operations = [
        migrations.AddField(
            model_name="usuario",
            name="rol",
            field=models.CharField(
                choices=[("administrador", "Administrador"), ("usuario", "Usuario normal")],
                default="usuario",
                max_length=20,
            ),
        ),
        migrations.RunPython(marcar_administradores, migrations.RunPython.noop),
    ]
