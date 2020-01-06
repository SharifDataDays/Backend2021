# Generated by Django 2.2.8 on 2019-12-27 15:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0004_remove_questionsubmission_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='score',
            name='question_submission',
            field=models.OneToOneField(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='score', to='contest.QuestionSubmission'),
            preserve_default=False,
        ),
    ]