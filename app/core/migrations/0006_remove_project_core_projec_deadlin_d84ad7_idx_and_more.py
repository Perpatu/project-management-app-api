# Generated by Django 4.2.4 on 2023-08-24 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_remove_file_department'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='project',
            name='core_projec_deadlin_d84ad7_idx',
        ),
        migrations.AddIndex(
            model_name='project',
            index=models.Index(fields=['deadline', 'number'], name='core_projec_deadlin_c3ad60_idx'),
        ),
    ]