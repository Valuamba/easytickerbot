# Generated by Django 3.1.3 on 2020-12-03 02:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tickets", "0005_auto_20201202_0034"),
    ]

    operations = [
        migrations.RemoveField(model_name="ticket", name="is_returned",),
        migrations.AddField(
            model_name="ticket",
            name="status",
            field=models.CharField(
                choices=[
                    ("created", "Created"),
                    ("payed", "Payed"),
                    ("payed", "Returned"),
                ],
                default="created",
                max_length=100,
            ),
        ),
    ]
