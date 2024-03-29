# Generated by Django 3.1.3 on 2020-12-17 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tickets", "0022_ticketcategory_is_hidden"),
    ]

    operations = [
        migrations.AddField(
            model_name="ticketselfie",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Не обработано"),
                    ("confirmed", "Одобрено"),
                    ("rejected", "Отклонено"),
                ],
                default="pending",
                max_length=100,
            ),
        ),
    ]
