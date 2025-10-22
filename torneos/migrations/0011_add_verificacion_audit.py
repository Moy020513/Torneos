# Generated manually: add verificado_por and fecha_verificacion to Jugador
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('torneos', '0009_add_jugador_verificado'),
    ]

    operations = [
        migrations.AddField(
            model_name='jugador',
            name='verificado_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='jugadores_verificados', to='auth.user'),
        ),
        migrations.AddField(
            model_name='jugador',
            name='fecha_verificacion',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
