from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework import status

from apps.contest.permissions import (
    UserHasTeam, UserHasTeamTasks, ProfileCompleted, TeamFinalized,
    TrialSubmissionOpen
)
from apps.contest.services.trial_services.trial_submit_validation import \
    TrialSubmitValidation
from apps.contest.tasks import judge_trials
from apps.contest.parsers import MyMultiPartParser

from . import models as contest_models, serializers
from apps.contest.services.trial_services import trial_maker


class ContestListAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ContestSerializer
    queryset = contest_models.Contest.objects.filter(
        start_time__lt=timezone.now()).order_by('order')

    def get(self, request):
        data = self.get_serializer(self.get_queryset(), many=True).data
        return Response(data={'contests': data})


class ContestAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated, UserHasTeam, ProfileCompleted,
                          ]  # TeamFinalized]
    serializer_class = serializers.ContestSerializer
    queryset = contest_models.Contest.objects.filter(
        start_time__lt=timezone.now()).order_by('order')

    def get(self, request, contest_id):
        contest = get_object_or_404(self.get_queryset(), id=contest_id)
        data = self.get_serializer(contest).data
        return Response(data={'contest': data})


class MilestoneAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated, UserHasTeam, UserHasTeamTasks,
                          ProfileCompleted, ]  # TeamFinalized]
    queryset = contest_models.Milestone.objects.filter(
        start_time__lt=timezone.now()).order_by('order')
    serializer_class = serializers.MilestoneSerializer

    def get_serializer_context(self):
        return {'team': self.team}

    def check_existance(self, contest_id, milestone_id):
        contest = get_object_or_404(contest_models.Contest, id=contest_id)
        milestone = get_object_or_404(contest_models.Milestone,
                                      pk=milestone_id)
        if milestone.contest != contest:
            raise NotFound('milestone is unrelated to contest')
        return contest, milestone

    def get(self, request, contest_id, milestone_id):
        contest, milestone = self.check_existance(contest_id, milestone_id)
        self.team = request.user.participant.teams.get(contest=contest)
        data = self.get_serializer(milestone).data
        return Response(data={'milestone': data}, status=status.HTTP_200_OK)


class TaskAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated, UserHasTeam, UserHasTeamTasks,
                          ProfileCompleted, TeamFinalized, TrialSubmissionOpen]
    queryset = contest_models.Task.objects.filter(
        milestone__start_time__lt=timezone.now()).order_by('order')
    serializer_class = serializers.TaskSerializer

    def get_serializer_context(self):
        return {
            'team_task': self.team_task,
        }

    def check_existance(self, contest_id, milestone_id, task_id):
        contest = get_object_or_404(contest_models.Contest, id=contest_id)
        milestone = get_object_or_404(contest_models.Milestone,
                                      pk=milestone_id)
        task = get_object_or_404(contest_models.Task, id=task_id)
        if milestone.contest != contest:
            raise NotFound('milestone is unrelated to contest')
        if task.milestone != milestone:
            raise NotFound('task is unrelated to milestone')
        return contest, milestone, task

    def get(self, request, contest_id, milestone_id, task_id):
        contest, milestone, task = self.check_existance(
            contest_id, milestone_id, task_id)
        team = request.user.participant.teams.get(contest=contest)
        self.team_task = team.tasks.get(task_id=task_id)
        self.trials = list(self.team_task.trials.all())
        data = self.get_serializer(self.team_task.task).data
        return Response(data=data, status=status.HTTP_200_OK)

    def post(self, request, contest_id, milestone_id, task_id):
        contest, milestone, task = self.check_existance(
            contest_id, milestone_id, task_id)
        maker = trial_maker.TrialMaker(
            request, contest_id, milestone_id, task_id)
        trial, errors = maker.make_trial()
        if trial is None:
            return Response(data={'detail': errors},
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response(data={'detail': 'ok',
                              'trial_id': trial.id},
                        status=status.HTTP_200_OK)

    def put(self, request, contest_id, milestone_id, task_id):
        contest, milestone, task = self.check_existance(
            contest_id, milestone_id, task_id)
        team = request.user.participant.teams.get(contest=contest)
        team_task = team.tasks.get(task_id=task_id)
        team_task.content_finished = True
        team_task.save()
        return Response(data={'detail': 'done'}, status=status.HTTP_200_OK)


class TrialAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated, UserHasTeam, UserHasTeamTasks,
                          ProfileCompleted, TeamFinalized, TrialSubmissionOpen]
    parser_classes = (MyMultiPartParser,)
    serializer_class = serializers.TrialPostSerializer

    def check_existance(self, contest_id, milestone_id, task_id, trial_id):
        contest = get_object_or_404(contest_models.Contest, id=contest_id)
        milestone = get_object_or_404(
            contest_models.Milestone, pk=milestone_id)
        task = get_object_or_404(contest_models.Task, id=task_id)
        trial = get_object_or_404(contest_models.Trial, id=trial_id)
        if milestone.contest != contest:
            raise NotFound('milestone is unrelated to contest')
        if task.milestone != milestone:
            raise NotFound('task is unrelated to milestone')
        if trial.team_task.task != task:
            raise NotFound('trial is unrelated to task')
        return contest, milestone, task, trial

    def get(self, request, contest_id, milestone_id, task_id, trial_id):
        contest, milestone, task, trial = self.check_existance(
            contest_id, milestone_id, task_id, trial_id)
        team = request.user.participant.teams.get(contest=contest)
        team_task = team.tasks.get(task_id=task_id)
        if trial not in team_task.trials.all():
            return Response(data={'detail': 'This trial is not yours. bitch'},
                            status=status.HTTP_406_NOT_ACCEPTABLE)

        data = serializers.TrialSerializer(trial).data
        return Response(data=data, status=200)

    def post(self, request, contest_id, milestone_id, task_id, trial_id):
        contest, milestone, task, trial = self.check_existance(
            contest_id, milestone_id, task_id, trial_id)
        team = request.user.participant.teams.get(contest=contest)
        team_task = team.tasks.get(task_id=task_id)
        if trial not in team_task.trials.all():
            return Response(data={'detail': 'This trial is not yours. bitch'},
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        if trial.submit_time is not None:
            return Response(
                data={'detail': 'This trial has already been submitted.'},
                status=406)
        trial_submitter = TrialSubmitValidation(
            request, contest_id, milestone_id, task_id, trial_id)
        trial, valid, errors = trial_submitter.validate()
        if not valid:
            return Response(data={'errors': errors},
                            status=status.HTTP_406_NOT_ACCEPTABLE)

        if trial_submitter.final_submit:
            trial.submit_time = timezone.now()
            trial.save()
            judge_trials.delay(trial.pk)
        else:
            trial.save()

        return Response(data={'detail': 'Trial submitted!'},
                        status=status.HTTP_200_OK)
