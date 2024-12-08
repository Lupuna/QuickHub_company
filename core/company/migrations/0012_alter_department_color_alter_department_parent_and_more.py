# Generated by Django 5.1.1 on 2024-11-26 09:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0011_alter_department_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='color',
            field=models.CharField(default='rgb(199,217,167)', max_length=20),
        ),
        migrations.AlterField(
            model_name='department',
            name='parent',
            field=models.ForeignKey(blank=True, help_text='connection with department parent', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='company.department'),
        ),
        migrations.AlterField(
            model_name='project',
            name='company',
            field=models.ForeignKey(help_text='connection with Company', on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='company.company'),
        ),
    ]
