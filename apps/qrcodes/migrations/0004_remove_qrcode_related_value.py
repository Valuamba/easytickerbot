# Generated by Django 3.1.3 on 2020-12-07 10:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("qrcodes", "0003_auto_20201206_1452"),
        ("tickets", "0014_auto_20201207_1119"),
    ]

    operations = [
        migrations.RemoveField(model_name="qrcode", name="related_value",),
    ]
