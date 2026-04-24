from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('torneos', '0032_partidoeliminatoria_arbitro'),
    ]

    operations = [
        migrations.AddField(
            model_name='eliminatoria',
            name='modalidad',
            field=models.CharField(
                choices=[('ida_vuelta', 'Ida y vuelta'), ('un_partido', 'A un partido')],
                default='ida_vuelta',
                max_length=20,
            ),
        ),
    ]
