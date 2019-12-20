# Generated by Django 2.2.8 on 2019-12-20 08:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('title', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Milestone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('title', models.CharField(max_length=100)),
                ('team_size', models.PositiveSmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='QuestionRecipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_type', models.CharField(choices=[('single_answer', 'Single Answer'), ('multi_answer', 'Multi Answer'), ('single_select', 'Single Select'), ('multi_select', 'Multi Select'), ('file_upload', 'File Upload'), ('manual_judgment', 'Manual Judgment'), ('numeric_range', 'Numeric Range')], max_length=20)),
                ('priority', models.PositiveSmallIntegerField()),
                ('count', models.PositiveSmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='QuestionSubmission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.TextField()),
                ('score', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.CharField(max_length=200, unique=True)),
                ('max_trials_count', models.PositiveSmallIntegerField(default=3)),
                ('trial_cooldown', models.PositiveSmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='TeamTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content_finished', models.BooleanField(default=False)),
                ('last_trial_time', models.DateTimeField(blank=True, null=True)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_tasks', to='contest.Task')),
            ],
        ),
        migrations.CreateModel(
            name='TrialRecipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='trial_recipe', to='contest.Task')),
            ],
        ),
        migrations.CreateModel(
            name='Trial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.PositiveSmallIntegerField(default=0)),
                ('due_time', models.DateTimeField()),
                ('start_time', models.DateTimeField(auto_now_add=True)),
                ('submit_time', models.DateTimeField(blank=True, null=True)),
                ('team_task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trials', to='contest.TeamTask')),
            ],
        ),
    ]
