# Generated by Django 3.1.3 on 2021-02-08 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tickets", "0034_ticket_payment_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="ticketcategory",
            name="time_end",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
