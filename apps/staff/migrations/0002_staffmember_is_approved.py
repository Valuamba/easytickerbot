# Generated by Django 3.1.3 on 2020-12-08 11:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("staff", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="staffmember",
            name="is_approved",
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
