# Generated by Django 4.2.5 on 2023-10-01 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_user_address'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ['last_name']},
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['last_name'], name='core_user_last_na_cc993d_idx'),
        ),
    ]
