# Generated by Django 5.1.1 on 2024-12-03 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0013_alter_department_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='color',
            field=models.CharField(default='rgb(219,209,173)', max_length=20),
        ),
    ]
