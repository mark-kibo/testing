# Generated by Django 4.1.1 on 2023-03-27 08:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bookparking', '0006_remove_payout_currency_alter_payout_payment_id_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Payout',
        ),
    ]