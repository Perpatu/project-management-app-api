# Generated by Django 4.2.5 on 2023-09-06 06:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_file_departments'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='queuelogic',
            name='chosen',
        ),
    ]