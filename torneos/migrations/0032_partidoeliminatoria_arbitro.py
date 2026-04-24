from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('torneos', '0031_torneo_config_registro_representantes'),
    ]

    operations = [
        migrations.AddField(
            model_name='partidoeliminatoria',
            name='arbitro',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name='partidos_eliminatoria',
                to='torneos.arbitro',
            ),
        ),
    ]
