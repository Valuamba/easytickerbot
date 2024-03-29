# Generated by Django 3.1.3 on 2020-11-30 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="QrCode",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("ticket", "Билет"),
                            ("staff", "Персонал"),
                            ("staff_invite", "Инвайт для персонала"),
                            ("promo", "Промо"),
                        ],
                        max_length=100,
                    ),
                ),
                ("token", models.CharField(max_length=500, unique=True)),
                (
                    "related_value",
                    models.CharField(blank=True, default="", max_length=500),
                ),
            ],
        ),
    ]
