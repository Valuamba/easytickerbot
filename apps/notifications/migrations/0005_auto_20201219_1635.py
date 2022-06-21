# Generated by Django 3.1.3 on 2020-12-19 16:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tickets", "0024_auto_20201217_1525"),
        ("staff", "0013_auto_20201213_1457"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("notifications", "0004_auto_20201208_1123"),
    ]

    operations = [
        migrations.RemoveField(model_name="broadcastnotification", name="created_by",),
        migrations.AddField(
            model_name="broadcastnotification",
            name="organizer",
            field=models.ForeignKey(
                default=1,
                limit_choices_to={"role": "organizer"},
                on_delete=django.db.models.deletion.CASCADE,
                to="management.adminaccount",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="broadcastnotification",
            name="ticket_category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="tickets.ticketcategory",
            ),
        ),
        migrations.AddField(
            model_name="broadcastnotification",
            name="type",
            field=models.CharField(
                choices=[
                    ("to_all", "Всем"),
                    ("to_staff", "Персоналу"),
                    ("to_guests", "Гостям"),
                ],
                default="to_staff",
                max_length=100,
            ),
        ),
        migrations.AlterField(
            model_name="broadcastnotification",
            name="staff_category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="staff.staffcategory",
            ),
        ),
    ]
