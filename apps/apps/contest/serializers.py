import datetime

from django.utils import timezone
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework import serializers

from apps.participation.serializers import TeamSerializer
from apps.question.serializers import QuestionPolymorphismSerializer
from apps.question.models import QuestionTypes
from apps.contest.models import Trial, TeamTask
from apps.resources.serializers import DocumentSerializer

from . import models as contest_models


class ScoreSerializer(ModelSerializer):
    class Meta:
        model = contest_models.Score
        fields = ['question_submission_id', 'number', 'status', 'info']


class QuestionSubmissionSerializer(ModelSerializer):
    question = QuestionPolymorphismSerializer()
    score = ScoreSerializer()

    answer = serializers.SerializerMethodField()

    class Meta:
        model = contest_models.QuestionSubmission
        fields = ['id', 'question', 'answer', 'score']

    def get_answer(self, obj):
        if obj.question.type == QuestionTypes.FILE_UPLOAD \
                and len(eval(obj.answer)) == 1:
            return ['/media/' + eval(obj.answer)[0]]
        return obj.answer


class QuestionSubmissionPostSerializer(ModelSerializer):
    id = serializers.ModelField(
        model_field=contest_models.QuestionSubmission()._meta.get_field('id'))
    answer = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = contest_models.QuestionSubmission
        fields = ['id', 'answer', 'has_file']


class TrialListSerializer(ModelSerializer):

    question_submissions = QuestionSubmissionSerializer(read_only=True,
                                                        many=True)
    scored = SerializerMethodField()

    class Meta:
        model = contest_models.Trial
        fields = ['id', 'score', 'due_time', 'start_time', 'submit_time',
                  'question_submissions', 'scored']

    def get_scored(self, obj):
        return False not in \
            [hasattr(qs, 'score') for qs in obj.question_submissions.all()]


class TaskSerializer(ModelSerializer):
    content = DocumentSerializer()

    trials = serializers.SerializerMethodField()
    content_finished = serializers.SerializerMethodField()
    can_create_trial = serializers.SerializerMethodField()
    trial_available = serializers.SerializerMethodField()
    trial_released = serializers.SerializerMethodField()

    # Absolute TOF
    rank = serializers.SerializerMethodField()

    class Meta:
        model = contest_models.Task
        fields = ['id', 'topic', 'trial_cooldown', 'content', 'scoring_type',
                  'trials', 'content_finished', 'max_trials_count',
                  'can_create_trial', 'trial_available', 'trial_time', 'rank',
                  'trial_released']

    def get_trials(self, obj):
        if 'team_task' not in self.context:
            return []
        return [TrialListSerializer(trial, read_only=True).data
                for trial in
                self.context.get('team_task').trials.all().order_by('id')]

    def get_content_finished(self, obj):
        if 'team_task' not in self.context:
            return False
        return self.context.get('team_task').content_finished

    def get_can_create_trial(self, obj):
        if 'team_task' not in self.context:
            return False

        team_task = self.context.get('team_task')
        return (
            team_task.content_finished
            and
            (
                team_task.trials.count() < team_task.task.max_trials_count
                or
                team_task.task.max_trials_count == 0
            )
            and
            team_task.trials.filter(submit_time=None).count() == 0
            and
            (team_task.trials.order_by('submit_time').last()
                or Trial(
                    submit_time=(
                        timezone.now()
                        - datetime.timedelta(
                            hours=team_task.task.trial_cooldown+1
                        )
                    )
                )
             ).submit_time
            + datetime.timedelta(hours=team_task.task.trial_cooldown)
            < timezone.now()
        )

    def get_trial_available(self, obj):
        if 'team_task' not in self.context:
            return False

        team_task = self.context.get('team_task')
        return hasattr(team_task.task, 'trial_recipe') \
            and team_task.task.trial_recipe is not None

    def get_trial_released(self, obj):
        if 'team_task' not in self.context:
            return False

        team_task = self.context.get('team_task')
        return (
            obj.trial_released
            or
            (True in [p.user.is_staff for p in
                      team_task.team.participants.all()])
        )

    def get_rank(self, obj):
        if 'team_task' not in self.context:
            return 'NaN'

        team_task = self.context.get('team_task')
        try:
            return sorted([t.final_score for t in
                           TeamTask.objects.filter(task=team_task.task)
                           if t.final_score is not None],
                          reverse=True).index(team_task.final_score) + 1
        except Exception:
            return 'NaN'


class MilestoneSerializer(ModelSerializer):

    tasks = serializers.SerializerMethodField()

    class Meta:
        model = contest_models.Milestone
        fields = ['id', 'title', 'start_time', 'end_time', 'tasks',
                  'description', 'image']

    def get_tasks(self, obj):
        tasks = []
        for task in obj.tasks.all().order_by('order'):
            team_task = None
            if 'team' in self.context:
                team_task = self.context.get('team').tasks.get(task=task)
            tasks.append(
                    TaskSerializer(
                        task,
                        context={'team_task': team_task},
                        read_only=True
                    ).data
                )
        return tasks


class ContestSerializer(ModelSerializer):
    milestones = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = contest_models.Contest
        fields = ['id', 'title', 'team_size', 'start_time', 'end_time',
                  'milestones', 'rules', 'description']


class ContestAsAListItemSerializer(ModelSerializer):
    class Meta:
        model = contest_models.Contest
        fields = ['id', 'title', 'start_time', 'end_time', 'rules',
                  'description']


class TrialSerializer(ModelSerializer):
    question_submissions = QuestionSubmissionSerializer(
        many=True, read_only=True)
    scored = SerializerMethodField()

    class Meta:
        model = contest_models.Trial
        fields = ['id', 'score', 'question_submissions', 'due_time',
                  'start_time', 'submit_time', 'scored']

    def get_scored(self, obj):
        return False not in \
            [hasattr(qs, 'score') for qs in obj.question_submissions.all()]


class TrialPostSerializer(ModelSerializer):
    id = serializers.ModelField(
        model_field=contest_models.Trial()._meta.get_field('id'))
    question_submissions = QuestionSubmissionPostSerializer(many=True)
    final_submit = serializers.BooleanField(default=False)

    class Meta:
        model = contest_models.Trial
        fields = ['id', 'question_submissions', 'final_submit']

    def validate(self, data):
        tf = contest_models.Trial.objects.filter(id=data['id'])
        if tf.count() != 1:
            raise serializers.ValidationError('Trial does not exists')
        trial = tf.get()
        qss = trial.question_submissions.all()
        for qs in data['question_submissions']:
            qsf = qss.filter(id=qs['id'])
            if qsf.count() != 1:
                raise serializers.ValidationError(
                    'QuestionSubmission doest not exists')
        return data

    def save(self):
        trial = contest_models.Trial.objects.get(id=self.validated_data['id'])
        qss = trial.question_submissions.all()
        for qs in self.validated_data['question_submissions']:
            q = qss.get(id=qs['id'])
            q.answer = str(qs['answer'])
            q.save()


class TeamTaskSerializer(ModelSerializer):
    task = TaskSerializer()
    team = TeamSerializer()

    class Meta:
        model = contest_models.TeamTask
        fields = ['id', 'contest_finished', 'last_trial_time', 'team', 'task']
