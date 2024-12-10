# Generated by Django 5.1.1 on 2024-12-10 07:32

import django.core.validators
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0015_alter_department_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='color',
            field=models.CharField(default='rgb(168,198,196)', max_length=20),
        ),
        migrations.AddField(
            model_name='project',
            name='creation_date',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='project',
            name='date_of_update',
            field=models.DateField(auto_now=True),
        ),
        migrations.AddField(
            model_name='project',
            name='departments',
            field=models.ManyToManyField(help_text='connection with Department', related_name='departments', to='company.department'),
        ),
        migrations.AddField(
            model_name='project',
            name='priority',
            field=models.PositiveSmallIntegerField(choices=[(0, 'High'), (1, 'Medium'), (2, 'Low')], default=1, validators=[django.core.validators.MaxValueValidator(5)]),
        ),
        migrations.AlterField(
            model_name='department',
            name='color',
            field=models.CharField(default='rgb(202,203,205)', max_length=20),
        ),
    ]