# Generated by Django 2.2.8 on 2019-12-26 22:57

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
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('team_size', models.PositiveSmallIntegerField()),
                ('title', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Milestone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('title', models.CharField(max_length=100)),
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
                ('question_priority', models.PositiveSmallIntegerField()),
                ('answer', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.FloatField(default=0)),
                ('status', models.CharField(choices=[('undefined', 'undefined'), ('scored', 'scored'), ('queued', 'queued'), ('judging', 'judging'), ('failed', 'failed'), ('error', 'error')], default='undefined', max_length=10)),
                ('info', models.CharField(blank=True, default='', max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.CharField(max_length=200, unique=True)),
                ('max_trials_count', models.PositiveSmallIntegerField(default=3)),
                ('trial_cooldown', models.PositiveSmallIntegerField()),
                ('trial_time', models.PositiveSmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='TeamTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content_finished', models.BooleanField(default=False)),
                ('final_score', models.FloatField(blank=True, null=True)),
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
                ('due_time', models.DateTimeField()),
                ('start_time', models.DateTimeField(auto_now_add=True)),
                ('submit_time', models.DateTimeField(blank=True, null=True)),
                ('score', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='trial', to='contest.Score')),
                ('team_task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trials', to='contest.TeamTask')),
            ],
        ),
    ]