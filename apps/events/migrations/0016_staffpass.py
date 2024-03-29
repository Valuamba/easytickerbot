# Generated by Django 3.1.3 on 2020-12-08 11:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("qrcodes", "0004_remove_qrcode_related_value"),
        ("staff", "0002_staffmember_is_approved"),
        ("events", "0015_event_staff_categories"),
    ]

    operations = [
        migrations.CreateModel(
            name="StaffPass",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="events.event"
                    ),
                ),
                (
                    "qr_code",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="qrcodes.qrcode"
                    ),
                ),
                (
                    "staff_member",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="staff.staffmember",
                    ),
                ),
            ],
            options={"abstract": False},
        ),
    ]
