from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User
from evaluation.models import JuryAssignment
from teams.models import Team
from tournaments.models import Round, Submission, Tournament
from backend.auth import authenticate

class ManualJuryAssignmentApiTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin_eval', email='admin_eval@example.com', password='TestPass123!', role='admin')
        self.non_admin = User.objects.create_user(username='team_eval', email='team_eval@example.com', password='TestPass123!', role='team')
        self.jury1 = User.objects.create_user(username='jury1_eval', email='jury1_eval@example.com', password='TestPass123!', role='jury')
        self.jury2 = User.objects.create_user(username='jury2_eval', email='jury2_eval@example.com', password='TestPass123!', role='jury')
        self.jury3 = User.objects.create_user(username='jury3_eval', email='jury3_eval@example.com', password='TestPass123!', role='jury')
        self.organizer = User.objects.create_user(username='organizer_eval', email='organizer_eval@example.com', password='TestPass123!', role='organizer')
        captain = User.objects.create_user(username='captain_eval', email='captain_eval@example.com', password='TestPass123!', role='team')
        now = timezone.now()
        tournament = Tournament.objects.create(name='Eval Tournament', start_date=now - timedelta(days=2), end_date=now + timedelta(days=2), status=Tournament.STATUS_RUNNING, created_by=self.organizer)
        self.round_obj = Round.objects.create(tournament=tournament, name='Round 1', start_date=now - timedelta(days=1), end_date=now + timedelta(hours=12), status=Round.STATUS_SUBMISSION_CLOSED, criteria=[{'id': 'backend', 'name': 'Backend', 'max_score': 10}])
        self.team = Team.objects.create(name='Team Eval', email='team@example.com', captain=captain, is_public=True)
        captain2 = User.objects.create_user(username='captain_eval_2', email='captain_eval_2@example.com', password='TestPass123!', role='team')
        self.team2 = Team.objects.create(name='Team Eval 2', email='team2@example.com', captain=captain2, is_public=True)
        self.submission1 = Submission.objects.create(team=self.team, round=self.round_obj, github_url='https://github.com/example/repo1', created_by=captain)
        self.submission2 = Submission.objects.create(team=self.team2, round=self.round_obj, github_url='https://github.com/example/repo2', created_by=captain2)

    def test_assign_jury_plain_array_replaces_existing_assignments(self):
        JuryAssignment.objects.create(submission=self.submission1, jury=self.jury3)
        payload = [{'submission': self.submission1.id, 'jury': [self.jury1.id, self.jury2.id]}, {'submission': self.submission2.id, 'jury': [self.jury1.id, self.jury2.id]}]
        authenticate(self.client, self.admin)
        response = self.client.post(reverse('ninja-api:round_assign_jury', kwargs={'round_id': self.round_obj.id}), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(JuryAssignment.objects.filter(submission__round=self.round_obj).count(), 4)

    def test_jury_can_list_own_assignments(self):
        own_assignment = JuryAssignment.objects.create(submission=self.submission1, jury=self.jury1)
        JuryAssignment.objects.create(submission=self.submission2, jury=self.jury2)
        authenticate(self.client, self.jury1)

        response = self.client.get(reverse('ninja-api:jury-assignments'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item['id'] for item in response.json()['items']], [own_assignment.id])

    def test_jury_can_create_evaluation_with_typed_scores(self):
        assignment = JuryAssignment.objects.create(submission=self.submission1, jury=self.jury1)
        authenticate(self.client, self.jury1)
        payload = {
            'tournament_id': self.round_obj.tournament_id,
            'assignment': assignment.id,
            'scores': [{'criterion_id': 'backend', 'score': 8}],
            'comment': 'Good work',
        }

        response = self.client.post(
            reverse('ninja-api:jury_evaluate_create'),
            payload,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['scores'], [
            {'criterion_id': 'backend', 'criterion_name': 'Backend', 'score': 8},
        ])

    def test_assign_jury_requires_full_submission_coverage(self):
        payload = [{'submission': self.submission1.id, 'jury': [self.jury1.id]}]
        authenticate(self.client, self.admin)
        response = self.client.post(reverse('ninja-api:round_assign_jury', kwargs={'round_id': self.round_obj.id}), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_assign_jury_requires_same_jury_count(self):
        payload = [{'submission': self.submission1.id, 'jury': [self.jury1.id]}, {'submission': self.submission2.id, 'jury': [self.jury1.id, self.jury2.id]}]
        authenticate(self.client, self.admin)
        response = self.client.post(reverse('ninja-api:round_assign_jury', kwargs={'round_id': self.round_obj.id}), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_assign_jury_rejects_non_jury_user(self):
        payload = [{'submission': self.submission1.id, 'jury': [self.non_admin.id]}, {'submission': self.submission2.id, 'jury': [self.non_admin.id]}]
        authenticate(self.client, self.admin)
        response = self.client.post(reverse('ninja-api:round_assign_jury', kwargs={'round_id': self.round_obj.id}), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_assign_jury_rejects_when_round_not_submission_closed(self):
        self.round_obj.status = Round.STATUS_ACTIVE
        self.round_obj.save()
        payload = [{'submission': self.submission1.id, 'jury': [self.jury1.id]}, {'submission': self.submission2.id, 'jury': [self.jury1.id]}]
        authenticate(self.client, self.admin)
        response = self.client.post(reverse('ninja-api:round_assign_jury', kwargs={'round_id': self.round_obj.id}), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_assign_jury_admin_only(self):
        payload = [{'submission': self.submission1.id, 'jury': [self.jury1.id]}, {'submission': self.submission2.id, 'jury': [self.jury1.id]}]
        authenticate(self.client, self.non_admin)
        response = self.client.post(reverse('ninja-api:round_assign_jury', kwargs={'round_id': self.round_obj.id}), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_organizer_can_assign_jury_but_jury_cannot(self):
        payload = [{'submission': self.submission1.id, 'jury': [self.jury2.id]}, {'submission': self.submission2.id, 'jury': [self.jury2.id]}]

        authenticate(self.client, self.organizer)
        organizer_response = self.client.post(reverse('ninja-api:round_assign_jury', kwargs={'round_id': self.round_obj.id}), payload, format='json')
        self.assertEqual(organizer_response.status_code, status.HTTP_201_CREATED)

        authenticate(self.client, self.jury1)
        jury_response = self.client.post(reverse('ninja-api:round_assign_jury', kwargs={'round_id': self.round_obj.id}), payload, format='json')
        self.assertEqual(jury_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_available_jury_returns_all_by_default(self):
        JuryAssignment.objects.create(submission=self.submission1, jury=self.jury1)
        authenticate(self.client, self.admin)
        response = self.client.get(reverse('ninja-api:round_available_jury', kwargs={'round_id': self.round_obj.id}))
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = {item['id'] for item in data}
        self.assertEqual(returned_ids, {self.jury1.id, self.jury2.id, self.jury3.id})

    def test_available_jury_excludes_assigned_when_requested(self):
        JuryAssignment.objects.create(submission=self.submission1, jury=self.jury1)
        authenticate(self.client, self.admin)
        response = self.client.get(reverse('ninja-api:round_available_jury', kwargs={'round_id': self.round_obj.id}), {'include_assigned': 'false'})
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = {item['id'] for item in data}
        self.assertEqual(returned_ids, {self.jury2.id, self.jury3.id})
