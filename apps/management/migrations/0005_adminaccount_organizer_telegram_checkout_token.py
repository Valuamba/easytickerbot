# Generated by Django 3.1.3 on 2021-02-05 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("management", "0004_auto_20210127_0947"),
    ]

    operations = [
        migrations.AddField(
            model_name="adminaccount",
            name="organizer_telegram_checkout_token",
            field=models.CharField(blank=True, default="", max_length=1000),
        ),
    ]
