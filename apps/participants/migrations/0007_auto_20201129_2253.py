# Generated by Django 3.1.3 on 2020-11-29 22:53

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0002_auto_20201122_0746"),
        ("events", "0005_auto_20201129_1946"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("participants", "0006_auto_20201129_2250"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="ParticipantCategory", new_name="StaffCategory",
        ),
    ]
