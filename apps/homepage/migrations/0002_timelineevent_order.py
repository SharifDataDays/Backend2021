# Generated by Django 2.2.8 on 2019-12-26 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='timelineevent',
            name='order',
            field=models.SmallIntegerField(null=True, unique=True),
        ),
    ]
