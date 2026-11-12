import django.db.models.deletion
from django.db import migrations, models


def crear_roles(apps, schema_editor):
    Rol = apps.get_model("cuentas", "Rol")
    Rol.objects.get_or_create(codigo="administrador", defaults={"nombre": "Administrador"})
    Rol.objects.get_or_create(codigo="usuario", defaults={"nombre": "Usuario normal"})


def copiar_rol(apps, schema_editor):
    Rol = apps.get_model("cuentas", "Rol")
    Usuario = apps.get_model("cuentas", "Usuario")
    administrador = Rol.objects.get(codigo="administrador")
    normal = Rol.objects.get(codigo="usuario")
    for perfil in Usuario.objects.all():
        perfil.rol_nuevo = administrador if perfil.rol == "administrador" else normal
        perfil.save(update_fields=["rol_nuevo"])


def devolver_rol(apps, schema_editor):
    Usuario = apps.get_model("cuentas", "Usuario")
    for perfil in Usuario.objects.all():
        perfil.rol = perfil.rol_nuevo.codigo
        perfil.save(update_fields=["rol"])


class Migration(migrations.Migration):

    dependencies = [
        ("cuentas", "0005_opciones_de_los_modelos"),
    ]

    operations = [
        migrations.CreateModel(
            name="Rol",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("codigo", models.CharField(max_length=20, unique=True)),
                ("nombre", models.CharField(max_length=50)),
            ],
            options={
                "verbose_name": "rol",
                "verbose_name_plural": "roles",
                "db_table": "roles",
            },
        ),
        migrations.RunPython(crear_roles, migrations.RunPython.noop),
        migrations.AddField(
            model_name="usuario",
            name="rol_nuevo",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name="usuarios", to="cuentas.rol"),
        ),
        migrations.RunPython(copiar_rol, devolver_rol),
        migrations.RemoveField(
            model_name="usuario",
            name="rol",
        ),
        migrations.RenameField(
            model_name="usuario",
            old_name="rol_nuevo",
            new_name="rol",
        ),
        migrations.AlterField(
            model_name="usuario",
            name="rol",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="usuarios", to="cuentas.rol"),
        ),
    ]
