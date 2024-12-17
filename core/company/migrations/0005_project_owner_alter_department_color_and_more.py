# Generated by Django 5.1.1 on 2024-12-17 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0004_alter_department_color_alter_project_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='owner',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='department',
            name='color',
            field=models.CharField(default='rgb(168,198,173)', max_length=20),
        ),
        migrations.AlterField(
            model_name='project',
            name='color',
            field=models.CharField(default='rgb(171,180,158)', max_length=20),
        ),
    ]