from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def _assign_existing_interactions_user(apps, schema_editor):
    InteraccionIA = apps.get_model("apiInteracciones", "InteraccionIA")
    Usuario = apps.get_model("apiUsuarios", "Usuario")
    fallback_user = Usuario.objects.order_by("id").first()

    if fallback_user is None:
        return

    InteraccionIA.objects.filter(usuario__isnull=True).update(usuario=fallback_user)


class Migration(migrations.Migration):
    dependencies = [
        ("apiUsuarios", "0002_remove_usuario_rol_cliente_empleado_socio_and_more"),
        ("apiInteracciones", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="interaccionia",
            name="usuario",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="interacciones_ia",
                to=settings.AUTH_USER_MODEL,
                help_text="Usuario autenticado que realizó la interacción",
            ),
        ),
        migrations.RunPython(_assign_existing_interactions_user, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="interaccionia",
            name="usuario",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="interacciones_ia",
                to=settings.AUTH_USER_MODEL,
                help_text="Usuario autenticado que realizó la interacción",
            ),
        ),
    ]
