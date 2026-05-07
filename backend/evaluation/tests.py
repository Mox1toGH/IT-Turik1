from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from evaluation.models import JuryAssignment
from teams.models import Team
from tournaments.models import Round, Submission, Tournament


class ManualJuryAssignmentApiTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin_eval',
            email='admin_eval@example.com',
            password='TestPass123!',
            role='admin',
        )
        self.non_admin = User.objects.create_user(
            username='team_eval',
            email='team_eval@example.com',
            password='TestPass123!',
            role='team',
        )
        self.jury1 = User.objects.create_user(
            username='jury1_eval',
            email='jury1_eval@example.com',
            password='TestPass123!',
            role='jury',
        )
        self.jury2 = User.objects.create_user(
            username='jury2_eval',
            email='jury2_eval@example.com',
            password='TestPass123!',
            role='jury',
        )
        self.jury3 = User.objects.create_user(
            username='jury3_eval',
            email='jury3_eval@example.com',
            password='TestPass123!',
            role='jury',
        )

        self.organizer = User.objects.create_user(
            username='organizer_eval',
            email='organizer_eval@example.com',
            password='TestPass123!',
            role='organizer',
        )
        captain = User.objects.create_user(
            username='captain_eval',
            email='captain_eval@example.com',
            password='TestPass123!',
            role='team',
        )

        now = timezone.now()
        tournament = Tournament.objects.create(
            name='Eval Tournament',
            description='desc',
            start_date=now - timedelta(days=2),
            end_date=now + timedelta(days=2),
            status=Tournament.STATUS_RUNNING,
            created_by=self.organizer,
        )

        self.round_obj = Round.objects.create(
            tournament=tournament,
            name='Round 1',
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(hours=12),
            status=Round.STATUS_SUBMISSION_CLOSED,
            criteria=[{'id': 'backend', 'name': 'Backend', 'max_score': 10}],
        )

        self.team = Team.objects.create(
            name='Team Eval',
            email='team@example.com',
            captain=captain,
            is_public=True,
        )
        captain2 = User.objects.create_user(
            username='captain_eval_2',
            email='captain_eval_2@example.com',
            password='TestPass123!',
            role='team',
        )
        self.team2 = Team.objects.create(
            name='Team Eval 2',
            email='team2@example.com',
            captain=captain2,
            is_public=True,
        )
        self.submission1 = Submission.objects.create(
            team=self.team,
            round=self.round_obj,
            github_url='https://github.com/example/repo1',
            demo_video_url='https://youtu.be/demo1',
            created_by=captain,
        )
        self.submission2 = Submission.objects.create(
            team=self.team2,
            round=self.round_obj,
            github_url='https://github.com/example/repo2',
            demo_video_url='https://youtu.be/demo2',
            created_by=captain2,
        )

    def test_assign_jury_plain_array_replaces_existing_assignments(self):
        JuryAssignment.objects.create(submission=self.submission1, jury=self.jury3)

        payload = [
            {'submission': self.submission1.id, 'jury': [self.jury1.id, self.jury2.id]},
            {'submission': self.submission2.id, 'jury': [self.jury1.id, self.jury2.id]},
        ]

        self.client.force_authenticate(self.admin)
        response = self.client.post(
            reverse('round_assign_jury', kwargs={'pk': self.round_obj.id}),
            payload,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['created_assignments'], 4)
        pairs = set(
            JuryAssignment.objects.filter(submission__round=self.round_obj).values_list('submission_id', 'jury_id')
        )
        self.assertEqual(
            pairs,
            {
                (self.submission1.id, self.jury1.id),
                (self.submission1.id, self.jury2.id),
                (self.submission2.id, self.jury1.id),
                (self.submission2.id, self.jury2.id),
            },
        )

    def test_assign_jury_requires_full_submission_coverage(self):
        payload = [{'submission': self.submission1.id, 'jury': [self.jury1.id]}]
        self.client.force_authenticate(self.admin)
        response = self.client.post(reverse('round_assign_jury', kwargs={'pk': self.round_obj.id}), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('submission', response.data.get('details', {}))

    def test_assign_jury_requires_same_jury_count_per_submission(self):
        payload = [
            {'submission': self.submission1.id, 'jury': [self.jury1.id]},
            {'submission': self.submission2.id, 'jury': [self.jury1.id, self.jury2.id]},
        ]
        self.client.force_authenticate(self.admin)
        response = self.client.post(reverse('round_assign_jury', kwargs={'pk': self.round_obj.id}), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('jury', response.data.get('details', {}))

    def test_assign_jury_rejects_non_jury_user(self):
        payload = [
            {'submission': self.submission1.id, 'jury': [self.non_admin.id]},
            {'submission': self.submission2.id, 'jury': [self.non_admin.id]},
        ]
        self.client.force_authenticate(self.admin)
        response = self.client.post(reverse('round_assign_jury', kwargs={'pk': self.round_obj.id}), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('jury', response.data.get('details', {}))

    def test_assign_jury_rejects_when_round_not_submission_closed(self):
        self.round_obj.status = Round.STATUS_ACTIVE
        self.round_obj.save(update_fields=['status', 'updated_at'])
        payload = [
            {'submission': self.submission1.id, 'jury': [self.jury1.id]},
            {'submission': self.submission2.id, 'jury': [self.jury1.id]},
        ]
        self.client.force_authenticate(self.admin)
        response = self.client.post(reverse('round_assign_jury', kwargs={'pk': self.round_obj.id}), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_assign_jury_admin_only(self):
        payload = [
            {'submission': self.submission1.id, 'jury': [self.jury1.id]},
            {'submission': self.submission2.id, 'jury': [self.jury1.id]},
        ]
        self.client.force_authenticate(self.non_admin)
        response = self.client.post(reverse('round_assign_jury', kwargs={'pk': self.round_obj.id}), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_organizer_and_jury_can_assign_jury(self):
        for user in (self.organizer, self.jury1):
            with self.subTest(role=user.role):
                payload = [
                    {'submission': self.submission1.id, 'jury': [self.jury2.id]},
                    {'submission': self.submission2.id, 'jury': [self.jury2.id]},
                ]
                self.client.force_authenticate(user)
                response = self.client.post(
                    reverse('round_assign_jury', kwargs={'pk': self.round_obj.id}),
                    payload,
                    format='json',
                )
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_available_jury_returns_all_by_default(self):
        JuryAssignment.objects.create(submission=self.submission1, jury=self.jury1)
        self.client.force_authenticate(self.admin)
        response = self.client.get(reverse('round_available_jury', kwargs={'pk': self.round_obj.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = {item['id'] for item in response.data}
        self.assertEqual(returned_ids, {self.jury1.id, self.jury2.id, self.jury3.id})

    def test_available_jury_excludes_assigned_when_include_assigned_false(self):
        JuryAssignment.objects.create(submission=self.submission1, jury=self.jury1)
        self.client.force_authenticate(self.admin)
        response = self.client.get(
            reverse('round_available_jury', kwargs={'pk': self.round_obj.id}),
            {'include_assigned': 'false'},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = {item['id'] for item in response.data}
        self.assertEqual(returned_ids, {self.jury2.id, self.jury3.id})

    def test_available_jury_admin_only(self):
        self.client.force_authenticate(self.non_admin)
        response = self.client.get(reverse('round_available_jury', kwargs={'pk': self.round_obj.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
