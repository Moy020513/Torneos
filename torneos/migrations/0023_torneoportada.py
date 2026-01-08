from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('torneos', '0022_torneo_portada'),
    ]

    operations = [
        migrations.CreateModel(
            name='TorneoPortada',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imagen', models.ImageField(upload_to='torneos/portadas/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'gif'])])),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('torneo', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='portadas', to='torneos.torneo')),
            ],
        ),
    ]
