# Generated by Django 4.1.1 on 2023-03-27 08:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bookparking', '0008_payout'),
    ]

    operations = [
        migrations.AddField(
            model_name='payout',
            name='client',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
