# Generated by Django 3.1.3 on 2021-01-25 20:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tickets", "0026_remove_ticketcategory_payment_confirmation_text"),
    ]

    operations = [
        migrations.AddField(
            model_name="ticket",
            name="guest_invite",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="tickets.guestinvite",
            ),
        ),
    ]
