# Generated by Django 3.1.3 on 2020-12-21 13:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0007_remove_notification_sended_at"),
    ]

    operations = [
        migrations.RenameField(
            model_name="notification", old_name="was_sended", new_name="was_sent",
        ),
    ]
