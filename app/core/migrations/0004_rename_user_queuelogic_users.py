# Generated by Django 4.2.7 on 2023-11-10 20:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_queuelogic_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='queuelogic',
            old_name='user',
            new_name='users',
        ),
    ]
