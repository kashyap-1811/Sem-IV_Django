# Generated by Django 4.2.19 on 2025-03-30 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0014_attendeerequest_is_attending'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendeerequest',
            name='is_attending',
            field=models.BooleanField(default=False),
        ),
    ]
