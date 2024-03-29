# Generated by Django 3.1.3 on 2020-12-07 03:38

from django.db import migrations


def migrate_qr_code_related_value_to_tickets(apps, schema_editor):
    QrCode = apps.get_model("qrcodes", "QrCode")
    Ticket = apps.get_model("tickets", "Ticket")

    for qr_code in QrCode.objects.filter(type="ticket"):
        try:
            ticket = Ticket.objects.get(id=int(qr_code.related_value))
        except Ticket.DoesNotExist:
            continue

        ticket.qr_code = qr_code
        ticket.save(update_fields=("qr_code",))


class Migration(migrations.Migration):

    dependencies = [
        ("tickets", "0012_ticket_qr_code"),
    ]

    operations = [
        migrations.RunPython(migrate_qr_code_related_value_to_tickets),
    ]
