# Generated by Django 3.1.3 on 2020-12-01 16:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("locations", "0006_auto_20201129_1946"),
    ]

    operations = [
        migrations.RemoveField(model_name="sublocation", name="location_owner",),
    ]
