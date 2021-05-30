from rest_framework import permissions

from apps.participation.models import Team, Participant
from apps.contest.models import Contest, Milestone, Task, TeamTask


class UserHasTeam(permissions.BasePermission):

    message = "User has no team in requested contest"

    def has_permission(self, request, view):
        if not hasattr(request.user, 'participant'):
            Participant.objects.create(user=request.user)

        try:
            contest = Contest.objects.filter(id=view.kwargs['contest_id'])
        except KeyError:
            return True

        if contest.count() == 0:
            return False
        contest = contest.get()

        if request.user.participant.teams.filter(contest=contest).count() == 0:
            Team.get_team(request.user.participant, contest)

        if not contest.released:
            if request.user.is_staff:
                return True
            return False

        return True


class UserHasTeamTasks(permissions.BasePermission):

    message = "user cannot participate in this milestone"

    def has_permission(self, request, view):
        try:
            milestone = Milestone.objects.filter(
                id=view.kwargs['milestone_id'])
        except KeyError:
            return True

        if milestone.count() == 0:
            return False
        milestone = milestone.get()

        if not milestone.released:
            if request.user.is_staff:
                return True
            return False

        team = request.user.participant.teams.get(contest=milestone.contest)
        team_tasks = team.tasks.all()
        for task in milestone.tasks.all():
            if task not in [tt.task for tt in team_tasks]:
                TeamTask.objects.create(
                    team=team, task=task, content_finished=False)
        return True


class ProfileCompleted(permissions.BasePermission):

    message = "complete your profile first"

    def has_permission(self, request, view):
        try:
            contest = Contest.objects.filter(id=view.kwargs['contest_id'])
        except KeyError:
            return True

        if contest.count() == 0:
            return False
        contest = contest.get()

        if contest.team_size == 1:
            return True

        return hasattr(request.user, 'profile') and \
            request.user.profile is not None and \
            request.user.profile.completed()


class TeamFinalized(permissions.BasePermission):

    message = "complete your team for this contest first"

    def has_permission(self, request, view):
        if request.method in ['GET', 'OPTIONS']:
            return True

        try:
            contest = Contest.objects.filter(id=view.kwargs['contest_id'])
        except KeyError:
            return True

        if contest.count() == 0:
            return False
        contest = contest.get()

        if contest.team_size == 1:
            return True

        team = request.user.participant.teams.get(contest=contest)
        return team.finalized()


class SignupOpen(permissions.BasePermission):

    message = "signup closed"

    def has_permission(self, request, view):
        if request.method in ['GET', 'OPTIONS']:
            return True

        try:
            contest = Contest.objects.filter(id=view.kwargs['contest_id'])
        except KeyError:
            return True

        if contest.count() == 0:
            return False
        contest = contest.get()

        return contest.signup_open


class TrialSubmissionOpen(permissions.BasePermission):

    message = "submission closed"

    def has_permission(self, request, view):
        if request.method in ['GET', 'OPTIONS']:
            return True

        try:
            task = Task.objects.filter(id=view.kwargs['task_id'])
        except KeyError:
            return True

        if task.count() == 0:
            return False
        task = task.get()

        return task.submit_open
