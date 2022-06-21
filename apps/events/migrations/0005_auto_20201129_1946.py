# Generated by Django 3.1.3 on 2020-11-29 19:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("participants", "0004_auto_20201129_1946"),
        ("events", "0004_auto_20201129_1434"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="participant_categories",
            field=models.ManyToManyField(
                related_name="events", to="participants.ParticipantCategory"
            ),
        ),
    ]
