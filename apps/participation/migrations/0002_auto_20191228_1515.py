# Generated by Django 2.2.8 on 2019-12-28 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('participation', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='participant',
            name='team',
        ),
        migrations.AddField(
            model_name='participant',
            name='teams',
            field=models.ManyToManyField(related_name='participants', to='participation.Team'),
        ),
    ]
