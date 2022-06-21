# Generated by Django 3.1.3 on 2020-12-02 00:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tickets", "0004_ticketcategory_is_active"),
    ]

    operations = [
        migrations.AddField(
            model_name="ticket",
            name="is_returned",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="ticket",
            name="category",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="tickets",
                to="tickets.ticketcategory",
            ),
        ),
    ]
