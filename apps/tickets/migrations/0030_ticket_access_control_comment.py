# Generated by Django 3.1.3 on 2021-01-27 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tickets", "0029_unifiedpass"),
    ]

    operations = [
        migrations.AddField(
            model_name="ticket",
            name="access_control_comment",
            field=models.TextField(blank=True, default=""),
        ),
    ]
