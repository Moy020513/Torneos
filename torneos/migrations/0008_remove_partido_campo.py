"""Remove campo field from Partido model

This migration removes the old CharField 'campo' which was kept in the DB
but removed from the model in code. Removing it here avoids IntegrityError
when creating Partidos without providing that column.
"""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('torneos', '0007_merge_20251020_1355'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='partido',
            name='campo',
        ),
    ]
