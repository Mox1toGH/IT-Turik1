from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User
from evaluation.models import JuryAssignment, SubmissionEvaluation
from teams.models import Team
from tournaments.models import Round, Submission, Tournament, TournamentTeamRegistration
from tournaments.services import mark_round_evaluated

class PassingCountTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user('admin_pc', 'admin_pc@example.com', 'TestPass123!', role='admin')
        self.team_user1 = User.objects.create_user('team_pc1', 'team_pc1@example.com', 'TestPass123!', role='team')
        self.team_user2 = User.objects.create_user('team_pc2', 'team_pc2@example.com', 'TestPass123!', role='team')
        now = timezone.now()
        self.tournament = Tournament.objects.create(name='PC Tournament', start_date=now - timedelta(days=2), end_date=now + timedelta(days=2), status=Tournament.STATUS_RUNNING, created_by=self.admin)
        self.round1 = Round.objects.create(tournament=self.tournament, name='Round 1', start_date=now - timedelta(days=2), end_date=now - timedelta(days=1), status=Round.STATUS_SUBMISSION_CLOSED, criteria=[{'id': 'crit1', 'name': 'Crit 1', 'max_score': 10}], passing_count=1)
        self.team1 = Team.objects.create(name='Team 1', email='team1@example.com', captain=self.team_user1)
        self.team2 = Team.objects.create(name='Team 2', email='team2@example.com', captain=self.team_user2)
        self.reg1 = TournamentTeamRegistration.objects.create(tournament=self.tournament, team=self.team1, is_active=True)
        self.reg2 = TournamentTeamRegistration.objects.create(tournament=self.tournament, team=self.team2, is_active=True)
        self.sub1 = Submission.objects.create(team=self.team1, round=self.round1, github_url='https://github.com/1', created_by=self.team_user1)
        self.sub2 = Submission.objects.create(team=self.team2, round=self.round1, github_url='https://github.com/2', created_by=self.team_user2)
        jury = User.objects.create_user('jury_pc', 'jury_pc@example.com', 'TestPass123!', role='jury')
        a1 = JuryAssignment.objects.create(submission=self.sub1, jury=jury)
        a2 = JuryAssignment.objects.create(submission=self.sub2, jury=jury)
        SubmissionEvaluation.objects.create(assignment=a1, scores=[{'criterion_id': 'crit1', 'criterion_name': 'Crit 1', 'score': 10}])
        SubmissionEvaluation.objects.create(assignment=a2, scores=[{'criterion_id': 'crit1', 'criterion_name': 'Crit 1', 'score': 5}])

    def test_apply_passing_count_eliminates_lower_ranked_teams(self):
        from evaluation.services import apply_passing_count
        apply_passing_count(self.round1)
        self.reg1.refresh_from_db()
        self.reg2.refresh_from_db()
        self.assertTrue(self.reg1.is_active)
        self.assertFalse(self.reg2.is_active)

    def test_apply_passing_count_none_does_nothing(self):
        from evaluation.services import apply_passing_count
        self.round1.passing_count = None
        self.round1.save()
        apply_passing_count(self.round1)
        self.reg1.refresh_from_db()
        self.reg2.refresh_from_db()
        self.assertTrue(self.reg1.is_active)
        self.assertTrue(self.reg2.is_active)

    def test_mark_round_evaluated_triggers_apply_passing_count(self):
        mark_round_evaluated(self.round1)
        self.reg1.refresh_from_db()
        self.reg2.refresh_from_db()
        self.assertTrue(self.reg1.is_active)
        self.assertFalse(self.reg2.is_active)

    def test_passing_status_endpoint(self):
        self.round1.status = Round.STATUS_EVALUATED
        self.round1.save()
        self.client.force_authenticate(self.admin)
        url = reverse('round_passing_status', kwargs={'pk': self.round1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['passing_count'], 1)

    def test_admin_can_manually_disqualify_team(self):
        self.client.force_authenticate(self.admin)
        url = reverse('tournament_registration_disqualification', kwargs={'pk': self.tournament.id, 'registration_pk': self.reg1.id})
        response = self.client.patch(url, {'action': 'disqualify', 'disqualification_reason': 'Violation'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.reg1.refresh_from_db()
        self.assertTrue(self.reg1.is_disqualified)

    def test_admin_can_reactivate_team(self):
        self.reg1.is_active = False
        self.reg1.is_disqualified = True
        self.reg1.save()
        self.client.force_authenticate(self.admin)
        url = reverse('tournament_registration_disqualification', kwargs={'pk': self.tournament.id, 'registration_pk': self.reg1.id})
        response = self.client.patch(url, {'action': 'reactivate'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.reg1.refresh_from_db()
        self.assertTrue(self.reg1.is_active)
        self.assertFalse(self.reg1.is_disqualified)

    def test_disqualification_action_is_required(self):
        self.client.force_authenticate(self.admin)
        url = reverse('tournament_registration_disqualification', kwargs={'pk': self.tournament.id, 'registration_pk': self.reg1.id})
        response = self.client.patch(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_disqualify_uses_default_reason_when_empty(self):
        self.client.force_authenticate(self.admin)
        url = reverse('tournament_registration_disqualification', kwargs={'pk': self.tournament.id, 'registration_pk': self.reg1.id})
        response = self.client.patch(url, {'action': 'disqualify', 'disqualification_reason': ' '}, format='json')
        self.reg1.refresh_from_db()
        self.assertEqual(self.reg1.disqualification_reason, 'Disqualified by admin')
