# Generated by Django 4.1.3 on 2023-02-16 09:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bookparking', '0003_rename_checkin_datetime_bookings_check_in_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bookings',
            old_name='check_out',
            new_name='checkout',
        ),
        migrations.RenameField(
            model_name='historicalbookings',
            old_name='check_out',
            new_name='checkout',
        ),
    ]
