# Generated by Django 3.1.3 on 2020-11-28 18:03

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("features", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="feature",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="feature",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
