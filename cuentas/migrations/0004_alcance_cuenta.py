from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cuentas", "0003_roles"),
    ]

    operations = [
        migrations.AddField(
            model_name="cuenta",
            name="alcance",
            field=models.CharField(
                choices=[("propia", "Cuenta propia"), ("grupo", "Cuenta del grupo")],
                default="grupo",
                max_length=10,
            ),
        ),
    ]
