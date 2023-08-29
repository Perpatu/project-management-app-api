# Generated by Django 4.2.4 on 2023-08-29 14:39

import core.models
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('name', models.CharField(blank=True, max_length=255)),
                ('first_name', models.CharField(blank=True, max_length=255)),
                ('last_name', models.CharField(blank=True, max_length=255)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('email', models.EmailField(blank=True, max_length=255)),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None)),
                ('address', models.CharField(blank=True, max_length=255)),
                ('date_add', models.DateField(auto_now_add=True)),
                ('color', models.CharField(blank=True, max_length=30)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='CommentFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('date_posted', models.DateTimeField(default=django.utils.timezone.now)),
                ('read', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-date_posted'],
            },
        ),
        migrations.CreateModel(
            name='CommentProject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('date_posted', models.DateTimeField(default=django.utils.timezone.now)),
                ('read', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-date_posted'],
            },
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('order', models.IntegerField(unique=True, validators=[django.core.validators.MinValueValidator(1)])),
                ('date_add', models.DateField(auto_now_add=True)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('destiny', models.CharField(choices=[('Project', 'Project'), ('Secretariat', 'Secretariat')], max_length=30)),
                ('file', models.FileField(upload_to=core.models.File.file_path)),
                ('date_add', models.DateField(default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateField()),
                ('deadline', models.DateField()),
                ('progress', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('priority', models.CharField(choices=[('High', 'High'), ('Normal', 'Normal'), ('Low', 'Low')], max_length=20)),
                ('status', models.CharField(choices=[('In design', 'In Design'), ('Started', 'Started'), ('Completed', 'Completed'), ('Suspended', 'Suspendded')], default='In design', max_length=20)),
                ('number', models.CharField(max_length=255)),
                ('secretariat', models.BooleanField(default=True)),
                ('invoiced', models.CharField(choices=[('YES', 'Yes'), ('YES (LACK OF INVOICE)', 'Lack Of Invoice'), ('NO', 'No')], default='NO', max_length=30)),
                ('date_add', models.DateField(default=django.utils.timezone.now)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.client')),
                ('manager', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['deadline'],
            },
        ),
        migrations.CreateModel(
            name='QueueLogic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chosen', models.BooleanField(default=False)),
                ('permission', models.BooleanField(default=False)),
                ('start', models.BooleanField(default=False)),
                ('paused', models.BooleanField(default=False)),
                ('end', models.BooleanField(default=False)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.department')),
                ('file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='queue', to='core.file')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.project')),
            ],
            options={
                'ordering': ['department__order'],
            },
        ),
        migrations.AddField(
            model_name='file',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='core.project'),
        ),
        migrations.AddField(
            model_name='file',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='department',
            index=models.Index(fields=['name'], name='core_depart_name_80d4fe_idx'),
        ),
        migrations.AddField(
            model_name='commentproject',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='core.project'),
        ),
        migrations.AddField(
            model_name='commentproject',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='commentfile',
            name='file',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='core.file'),
        ),
        migrations.AddField(
            model_name='commentfile',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='client',
            index=models.Index(fields=['name'], name='core_client_name_76d9ae_idx'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions'),
        ),
        migrations.AddIndex(
            model_name='queuelogic',
            index=models.Index(fields=['department'], name='core_queuel_departm_863cc1_idx'),
        ),
        migrations.AddIndex(
            model_name='project',
            index=models.Index(fields=['deadline'], name='core_projec_deadlin_d84ad7_idx'),
        ),
        migrations.AddIndex(
            model_name='project',
            index=models.Index(fields=['number'], name='core_projec_number_e2d484_idx'),
        ),
        migrations.AddIndex(
            model_name='file',
            index=models.Index(fields=['name'], name='core_file_name_02f7a3_idx'),
        ),
        migrations.AddIndex(
            model_name='file',
            index=models.Index(fields=['file'], name='core_file_file_4d9480_idx'),
        ),
        migrations.AddIndex(
            model_name='commentproject',
            index=models.Index(fields=['-date_posted'], name='core_commen_date_po_8ad06d_idx'),
        ),
        migrations.AddIndex(
            model_name='commentfile',
            index=models.Index(fields=['-date_posted'], name='core_commen_date_po_095064_idx'),
        ),
    ]
