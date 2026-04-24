from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('torneos', '0030_sancion'),
    ]

    operations = [
        migrations.AddField(
            model_name='torneo',
            name='bloquear_registro_jugadores_representante',
            field=models.BooleanField(
                default=False,
                help_text='Si esta activo, los representantes no pueden registrar nuevos jugadores.'
            ),
        ),
        migrations.AddField(
            model_name='torneo',
            name='max_jugadores_por_representante',
            field=models.PositiveIntegerField(
                default=16,
                help_text='Cantidad maxima de jugadores que puede registrar cada representante en este torneo.'
            ),
        ),
    ]
