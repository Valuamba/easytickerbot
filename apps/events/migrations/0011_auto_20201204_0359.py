# Generated by Django 3.1.3 on 2020-12-04 03:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0010_auto_20201204_0215"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="poster",
            field=models.ImageField(
                blank=True, null=True, upload_to="events/posters/%y/%m/%d"
            ),
        ),
    ]
