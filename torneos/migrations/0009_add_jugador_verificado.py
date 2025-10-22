# Generated manually: Add field verificado to Jugador
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('torneos', '0008_remove_partido_campo'),
    ]

    operations = [
        migrations.AddField(
            model_name='jugador',
            name='verificado',
            field=models.BooleanField(default=False, help_text='Indica si el jugador fue verificado por un administrador'),
        ),
    ]
