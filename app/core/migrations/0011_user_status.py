# Generated by Django 4.2.7 on 2023-11-12 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_project_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='status',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]