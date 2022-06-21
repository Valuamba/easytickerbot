# Generated by Django 3.1.3 on 2020-12-04 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tickets", "0010_ticketcategory_per_participant_limit"),
    ]

    operations = [
        migrations.AlterField(
            model_name="purchaseconfirmation",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Не обработано"),
                    ("confirmed", "Оплата подтверждена"),
                    ("rejected", "Отклонено"),
                    ("refund_requested", "Запрошен возврат"),
                    ("refund_performed", "Выполнен возврат"),
                ],
                default="pending",
                max_length=100,
            ),
        ),
        migrations.AlterField(
            model_name="ticket",
            name="status",
            field=models.CharField(
                choices=[
                    ("created", "Не оплачен"),
                    ("payed", "Оплачен"),
                    ("used", "Проход осуществлён"),
                    ("returned", "Выполнен возврат"),
                ],
                default="created",
                max_length=100,
            ),
        ),
    ]
