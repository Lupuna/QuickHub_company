# Generated by Django 5.1.1 on 2024-10-29 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0004_alter_projectposition_project_access_weight'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectposition',
            name='project_access_weight',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Setting up project parameters'), (2, 'Executing and assigning tasks'), (3, 'Executing tasks'), (4, 'Observer'), (5, 'Standard')], default=5, help_text='access level for the position'),
        ),
    ]
