# Generated by Django 3.1.3 on 2021-01-11 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tickets", "0024_auto_20201217_1525"),
    ]

    operations = [
        migrations.AddField(
            model_name="ticketcategory",
            name="payment_confirmation_text",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="ticketcategory",
            name="selfie_confirmed_text",
            field=models.TextField(blank=True, default=""),
        ),
    ]
