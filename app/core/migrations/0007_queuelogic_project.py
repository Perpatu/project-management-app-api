# Generated by Django 4.2.4 on 2023-08-27 15:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_queuelogic_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='queuelogic',
            name='project',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='core.project'),
            preserve_default=False,
        ),
    ]