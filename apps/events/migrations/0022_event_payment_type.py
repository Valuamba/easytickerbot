# Generated by Django 3.1.3 on 2021-02-22 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0021_event_selfie_rejected_text"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="payment_type",
            field=models.CharField(
                blank=True,
                choices=[("yoomoney", "YooMoney"), ("fondy", "Fondy")],
                default="",
                max_length=100,
            ),
        ),
    ]