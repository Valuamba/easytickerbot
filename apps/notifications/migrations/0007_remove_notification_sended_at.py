# Generated by Django 3.1.3 on 2020-12-20 13:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0006_auto_20201220_1229"),
    ]

    operations = [
        migrations.RemoveField(model_name="notification", name="sended_at",),
    ]