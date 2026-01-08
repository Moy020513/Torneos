from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('torneos', '0021_registroactividad'),
    ]

    operations = [
        migrations.AddField(
            model_name='torneo',
            name='portada',
            field=models.ImageField(
                blank=True,
                help_text='Imagen de portada que se muestra en la tarjeta del torneo',
                null=True,
                upload_to='torneos/portadas/',
                validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'gif'])],
            ),
        ),
    ]
