# Generated by Django 4.2.4 on 2023-08-22 05:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_user_first_name_alter_user_last_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='queuelogic',
            name='permission',
            field=models.BooleanField(default=False),
        ),
    ]