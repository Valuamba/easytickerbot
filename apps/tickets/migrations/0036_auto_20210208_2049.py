# Generated by Django 3.1.3 on 2021-02-08 20:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("tickets", "0035_ticketcategory_time_end"),
    ]

    operations = [
        migrations.RenameField(
            model_name="ticketcategory", old_name="time_end", new_name="lifetime_end",
        ),
    ]
