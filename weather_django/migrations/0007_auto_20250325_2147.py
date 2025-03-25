# Generated by Django 2.2.28 on 2025-03-25 21:47

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weather_django', '0006_userprofile_saved_locations'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='saved_locations',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=128), blank=True, default=list, size=None),
        ),
    ]
