from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from accounts.models import User
from evaluation.models import JuryAssignment
from tournaments.models import Submission, Round, Tournament
from teams.models import Team

class EvaluationRBACTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user('admin_rbac', 'admin@e.com', 'pass', role='admin', is_staff=True)
        self.jury = User.objects.create_user('jury_rbac', 'jury@e.com', 'pass', role='jury')
        self.user = User.objects.create_user('user_rbac', 'u@e.com', 'pass', role='team')
        
        self.team = Team.objects.create(name='RBAC Team', email='rbac@e.com', captain=self.user)
        from django.utils import timezone
        import datetime
        now = timezone.now()
        self.tournament = Tournament.objects.create(
            name='RBAC Tourney', 
            start_date=now - datetime.timedelta(days=1),
            end_date=now + datetime.timedelta(days=1),
            created_by=self.admin
        )
        self.round = Round.objects.create(tournament=self.tournament, name='R1')
        self.submission = Submission.objects.create(team=self.team, round=self.round, created_by=self.user)
        
        self.assignment = JuryAssignment.objects.create(submission=self.submission, jury=self.jury)
        self.url = reverse('jury_assignment_evaluate', kwargs={'pk': self.assignment.id})

    def test_unauthenticated_cannot_evaluate(self):
        response = self.client.post(self.url, {'scores': []}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_evaluate(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {'scores': []}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_cannot_evaluate_if_not_assigned(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.url, {'scores': []}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_assigned_jury_can_evaluate(self):
        self.client.force_authenticate(user=self.jury)
        # Even with validation errors, the status code shouldn't be 403
        response = self.client.post(self.url, {'scores': []}, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)
