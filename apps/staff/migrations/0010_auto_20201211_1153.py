# Generated by Django 3.1.3 on 2020-12-11 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("staff", "0009_staffmember_staff_invite"),
    ]

    operations = [
        migrations.AlterField(
            model_name="staffcategory",
            name="stereotype",
            field=models.CharField(
                blank=True,
                choices=[("access_control", "Пропускной контроль"), ("bar", "Бар")],
                max_length=500,
                null=True,
            ),
        ),
    ]