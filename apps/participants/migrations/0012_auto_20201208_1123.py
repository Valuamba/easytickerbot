# Generated by Django 3.1.3 on 2020-12-08 11:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("participants", "0011_auto_20201204_1907"),
    ]

    operations = [
        migrations.RemoveField(model_name="staffcategory", name="organizer",),
        migrations.RemoveField(model_name="staffcategory", name="parent",),
        migrations.RemoveField(model_name="participant", name="is_approved",),
        migrations.RemoveField(model_name="participant", name="organizer_account",),
        migrations.RemoveField(model_name="participant", name="staff_category",),
    ]
