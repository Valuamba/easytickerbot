# Generated by Django 3.1.3 on 2020-11-29 23:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0005_auto_20201129_1946"),
    ]

    operations = [
        migrations.RenameField(
            model_name="event",
            old_name="participant_categories",
            new_name="staff_categories",
        ),
    ]