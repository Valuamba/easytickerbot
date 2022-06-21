# Generated by Django 3.1.3 on 2020-11-19 21:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("management", "0002_auto_20201114_1527"),
    ]

    operations = [
        migrations.AlterField(
            model_name="adminaccount",
            name="role",
            field=models.CharField(
                choices=[
                    ("super_admin", "Суперадмин"),
                    ("location_owner", "Владелец локации"),
                    ("organizer", "Организатор"),
                ],
                max_length=100,
            ),
        ),
    ]