# Generated by Django 4.1.3 on 2023-02-26 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookparking', '0002_booking_has_expired'),
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=1000)),
            ],
        ),
        migrations.RemoveField(
            model_name='reserveuser',
            name='is_employee',
        ),
    ]
