from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('torneos', '0005_torneo_color1_torneo_color2_torneo_color3'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParticipacionJugador',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titular', models.BooleanField(default=True, help_text='¿Fue titular?')),
                ('minutos_jugados', models.PositiveIntegerField(blank=True, null=True)),
                ('observaciones', models.CharField(blank=True, max_length=255)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('jugador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participaciones', to='torneos.jugador')),
                ('partido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participaciones', to='torneos.partido')),
            ],
            options={
                'verbose_name': 'Participación de Jugador',
                'verbose_name_plural': 'Participaciones de Jugadores',
                'unique_together': {('jugador', 'partido')},
            },
        ),
    ]