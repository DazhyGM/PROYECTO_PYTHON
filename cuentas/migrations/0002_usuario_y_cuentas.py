import django.db.models.deletion
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import migrations, models


def crear_pruebas_y_vincular(apps, schema_editor):
    User = apps.get_model("auth", "User")
    Usuario = apps.get_model("cuentas", "Usuario")
    Cuenta = apps.get_model("cuentas", "Cuenta")
    pruebas, creado = User.objects.get_or_create(
        username="pruebas",
        defaults={"password": make_password("Login.2025")},
    )
    if not creado:
        pruebas.password = make_password("Login.2025")
        pruebas.save(update_fields=["password"])
    for user in User.objects.all():
        Usuario.objects.get_or_create(user=user)
    dueno = Usuario.objects.get(user=pruebas)
    Cuenta.objects.filter(usuario__isnull=True).update(usuario=dueno)


class Migration(migrations.Migration):

    dependencies = [
        ("cuentas", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Usuario",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="usuario",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="cuenta",
            name="usuario",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="cuentas.usuario",
            ),
        ),
        migrations.RunPython(crear_pruebas_y_vincular, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="cuenta",
            name="usuario",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="cuentas.usuario",
            ),
        ),
    ]
