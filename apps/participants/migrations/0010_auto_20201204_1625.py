# Generated by Django 3.1.3 on 2020-12-04 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("participants", "0009_staffcategory_is_access_control"),
    ]

    operations = [
        migrations.RemoveField(model_name="staffcategory", name="is_access_control",),
        migrations.AddField(
            model_name="staffcategory",
            name="stereotype",
            field=models.CharField(
                blank=True,
                choices=[("access_control", "Access control")],
                max_length=500,
                null=True,
            ),
        ),
    ]
