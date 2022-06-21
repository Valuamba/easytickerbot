# Generated by Django 3.1.3 on 2021-03-16 22:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0023_auto_20210222_1329"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="payment_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("yoomoney", "YooMoney"),
                    ("yoomoney_telegram", "YooMoney (Telegram)"),
                    ("fondy", "Fondy"),
                ],
                default="",
                max_length=100,
            ),
        ),
    ]