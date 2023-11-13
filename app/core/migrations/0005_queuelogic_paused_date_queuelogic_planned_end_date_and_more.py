# Generated by Django 4.2.7 on 2023-11-11 16:21

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_rename_user_queuelogic_users'),
    ]

    operations = [
        migrations.AddField(
            model_name='queuelogic',
            name='paused_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='queuelogic',
            name='planned_end_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='queuelogic',
            name='planned_start_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]