# Generated by Django 3.1.3 on 2021-01-29 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tickets", "0030_ticket_access_control_comment"),
    ]

    operations = [
        migrations.AddField(
            model_name="ticketcategory",
            name="additional_data_request",
            field=models.TextField(blank=True, default=""),
        ),
    ]
