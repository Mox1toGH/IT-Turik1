from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User
from evaluation.models import JuryAssignment, LeaderboardEntry, SubmissionEvaluation
from evaluation.leaderboard_service import compute_leaderboard, compute_tournament_leaderboard, save_leaderboard_snapshot
from teams.models import Team
from tournaments.models import Round, Submission, Tournament, TournamentTeamRegistration
from tournaments.services import mark_round_evaluated

class LeaderboardTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user('admin_lb', 'admin_lb@example.com', 'TestPass123!', role='admin')
        self.organizer = User.objects.create_user('organizer_lb', 'organizer_lb@example.com', 'TestPass123!', role='organizer')
        self.jury1 = User.objects.create_user('jury1_lb', 'jury1_lb@example.com', 'TestPass123!', role='jury')
        self.jury2 = User.objects.create_user('jury2_lb', 'jury2_lb@example.com', 'TestPass123!', role='jury')
        self.team_user = User.objects.create_user('team_lb', 'team_lb@example.com', 'TestPass123!', role='team')
        now = timezone.now()
        self.tournament = Tournament.objects.create(name='LB Tournament', start_date=now - timedelta(days=2), end_date=now + timedelta(days=2), status=Tournament.STATUS_RUNNING, created_by=self.organizer)
        self.round_obj = Round.objects.create(tournament=self.tournament, name='Qualifying', start_date=now - timedelta(days=2), end_date=now - timedelta(days=1), status=Round.STATUS_SUBMISSION_CLOSED, criteria=[{'id': 'innovation', 'name': 'Innovation', 'max_score': 10}])
        self.team1 = Team.objects.create(name='Team Alpha', email='alpha@example.com', captain=self.team_user, is_public=True)
        TournamentTeamRegistration.objects.create(tournament=self.tournament, team=self.team1, is_active=True)
        self.sub1 = Submission.objects.create(team=self.team1, round=self.round_obj, github_url='https://github.com/example/a', created_by=self.team_user)
        self.assign11 = JuryAssignment.objects.create(submission=self.sub1, jury=self.jury1)
        SubmissionEvaluation.objects.create(assignment=self.assign11, scores=[{'criterion_id': 'innovation', 'criterion_name': 'Innovation', 'score': 9}])

    def test_compute_leaderboard_returns_correct_rank_order(self):
        self.round_obj.status = Round.STATUS_EVALUATED
        self.round_obj.save()
        rankings = compute_leaderboard(self.round_obj.id)
        self.assertEqual(rankings[0]['team_id'], self.team1.id)
        self.assertEqual(rankings[0]['rank'], 1)

    def test_save_leaderboard_snapshot_is_idempotent(self):
        save_leaderboard_snapshot(self.tournament.id, self.round_obj.id)
        save_leaderboard_snapshot(self.tournament.id, self.round_obj.id)
        self.assertEqual(LeaderboardEntry.objects.filter(tournament=self.tournament, round=self.round_obj).count(), 1)

    def test_compute_tournament_leaderboard(self):
        rankings = compute_tournament_leaderboard(self.tournament.id)
        self.assertEqual(rankings[0]['team_id'], self.team1.id)

    def test_team_role_sees_jury_breakdown_null(self):
        self.round_obj.status = Round.STATUS_EVALUATED
        self.round_obj.save()
        self.client.force_authenticate(self.team_user)
        response = self.client.get(reverse('tournament_leaderboard', kwargs={'tournament_id': self.tournament.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data['rankings'][0]['rounds'][0]['jury_breakdown'])

    def test_admin_organizer_jury_see_jury_breakdown(self):
        self.round_obj.status = Round.STATUS_EVALUATED
        self.round_obj.save()
        for user in (self.admin, self.organizer, self.jury1):
            with self.subTest(role=user.role):
                self.client.force_authenticate(user)
                response = self.client.get(reverse('tournament_leaderboard', kwargs={'tournament_id': self.tournament.id}))
                self.assertIsNotNone(response.data['rankings'][0]['rounds'][0]['jury_breakdown'])

    def test_live_endpoint_returns_403_for_team_if_round_not_evaluated(self):
        self.round_obj.status = Round.STATUS_ACTIVE
        self.round_obj.save()
        self.client.force_authenticate(self.team_user)
        response = self.client.get(reverse('round_leaderboard', kwargs={'round_id': self.round_obj.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_mark_round_evaluated_eliminates_teams(self):
        self.round_obj.passing_count = 0
        self.round_obj.status = Round.STATUS_SUBMISSION_CLOSED
        self.round_obj.save()
        mark_round_evaluated(self.round_obj)
        reg = TournamentTeamRegistration.objects.get(tournament=self.tournament, team=self.team1)
        self.assertFalse(reg.is_active)

    def test_compute_leaderboard_excludes_disqualified_teams(self):
        TournamentTeamRegistration.objects.filter(tournament=self.tournament, team=self.team1).update(is_active=False, is_disqualified=True)
        rankings = compute_leaderboard(self.round_obj.id)
        self.assertEqual(len(rankings), 0)
