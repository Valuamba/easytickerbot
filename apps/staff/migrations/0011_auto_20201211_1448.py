# Generated by Django 3.1.3 on 2020-12-11 14:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("staff", "0010_auto_20201211_1153"),
    ]

    operations = [
        migrations.AlterField(
            model_name="staffmember",
            name="staff_category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="staff_members",
                to="staff.staffcategory",
            ),
        ),
    ]
