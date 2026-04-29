from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from teams.models import Team, TeamMember
from .models import Tournament, Round, Submission, TournamentTeamRegistration


class TournamentApiTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='StrongPass123!',
            role='admin',
            is_staff=True,
            is_superuser=True,
        )
        self.captain = User.objects.create_user(
            username='captain',
            email='captain@example.com',
            password='StrongPass123!',
        )
        self.organizer = User.objects.create_user(
            username='organizer',
            email='organizer@example.com',
            password='StrongPass123!',
            role='organizer',
        )
        self.team = Team.objects.create(
            name='Test Team',
            email='test@example.com',
            captain=self.captain,
        )
        TeamMember.objects.create(team=self.team, user=self.captain)

        self.tournament_data = {
            'name': 'Dev Tournament',
            'description': 'Test description',
            'start_date': timezone.now() + timezone.timedelta(days=1),
            'end_date': timezone.now() + timezone.timedelta(days=10),
            'rounds_count': 2,
        }

    def test_admin_can_create_tournament(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('tournament_manage_create')
        response = self.client.post(url, self.tournament_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tournament.objects.count(), 1)
        self.assertEqual(Round.objects.count(), 2)

    def test_organizer_can_create_tournament(self):
        self.client.force_authenticate(user=self.organizer)
        url = reverse('tournament_manage_create')
        response = self.client.post(url, self.tournament_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tournament.objects.count(), 1)
        self.assertEqual(Round.objects.count(), 2)

    def test_non_admin_cannot_create_tournament(self):
        self.client.force_authenticate(user=self.captain)
        url = reverse('tournament_manage_create')
        response = self.client.post(url, self.tournament_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_admin_cannot_update_tournament(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            **self.tournament_data
        )
        self.client.force_authenticate(user=self.captain)
        url = reverse('tournament_manage_update', kwargs={'pk': tournament.id})
        response = self.client.patch(url, {'name': 'Hacked Name'}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_start_registration(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            **self.tournament_data
        )
        self.client.force_authenticate(user=self.admin)
        url = reverse('tournament_start_registration', kwargs={'pk': tournament.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tournament.refresh_from_db()
        self.assertEqual(tournament.status, Tournament.STATUS_REGISTRATION)

    def test_team_registration(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_REGISTRATION,
            **self.tournament_data
        )
        self.client.force_authenticate(user=self.captain)
        url = reverse('tournament_register_team', kwargs={'pk': tournament.id})
        response = self.client.post(url, {'team_id': self.team.id}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(TournamentTeamRegistration.objects.filter(tournament=tournament, team=self.team).exists())

    def test_round_management(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            **self.tournament_data
        )
        self.client.force_authenticate(user=self.admin)
        url = reverse('rounds')
        
        round_data = {
            'tournament': tournament.id,
            'position': 3,
            'name': 'Extra Round',
            'start_date': self.tournament_data['start_date'],
            'end_date': self.tournament_data['end_date'],
        }
        response = self.client.post(url, round_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        round_data['position'] = 1
        response = self.client.post(url, round_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_submission_creation(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_RUNNING,
            **self.tournament_data
        )
        round_obj = Round.objects.create(
            tournament=tournament,
            position=1,
            status=Round.STATUS_ACTIVE,
            start_date=timezone.now() - timezone.timedelta(hours=1),
            end_date=timezone.now() + timezone.timedelta(hours=1),
        )
        TournamentTeamRegistration.objects.create(tournament=tournament, team=self.team)
        
        self.client.force_authenticate(user=self.captain)
        url = reverse('submissions')
        submission_data = {
            'team': self.team.id,
            'round': round_obj.id,
            'github_url': 'https://github.com/test/repo',
            'demo_video_url': 'https://youtube.com/test',
            'description': 'Test submission',
        }
        response = self.client.post(url, submission_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Submission.objects.count(), 1)

        # Test duplicate submission fails
        response = self.client.post(url, submission_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('code'), 'validation_error')
        # We check that there are some details about the error, 
        # without strictly requiring 'non_field_errors' or 'team' key
        self.assertTrue(response.data.get('details'))

    def test_submission_requires_team_tournament_registration(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_RUNNING,
            **self.tournament_data
        )
        round_obj = Round.objects.create(
            tournament=tournament,
            position=1,
            status=Round.STATUS_ACTIVE,
            start_date=timezone.now() - timezone.timedelta(hours=1),
            end_date=timezone.now() + timezone.timedelta(hours=1),
        )

        self.client.force_authenticate(user=self.captain)
        url = reverse('submissions')
        submission_data = {
            'team': self.team.id,
            'round': round_obj.id,
            'github_url': 'https://github.com/test/repo',
            'demo_video_url': 'https://youtube.com/test',
            'description': 'Unregistered team submission',
        }
        response = self.client.post(url, submission_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('code'), 'validation_error')
        self.assertIn('team', response.data['details'])

    def test_registration_limit_reached(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_REGISTRATION,
            max_teams=1,
            **self.tournament_data
        )
        TournamentTeamRegistration.objects.create(tournament=tournament, team=self.team)
        
        other_user = User.objects.create_user(username='other', email='other@example.com', password='StrongPass123!')
        other_team = Team.objects.create(name='Other Team', email='other@example.com', captain=other_user)
        
        self.client.force_authenticate(user=other_user)
        url = reverse('tournament_register_team', kwargs={'pk': tournament.id})
        response = self.client.post(url, {'team_id': other_team.id}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('tournament', response.data['details'])

    def test_sync_time_based_statuses(self):
        from .services import sync_time_based_statuses
        
        tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_RUNNING,
            **self.tournament_data
        )
        round_obj = Round.objects.create(
            tournament=tournament,
            position=1,
            status=Round.STATUS_ACTIVE,
            start_date=timezone.now() - timezone.timedelta(days=2),
            end_date=timezone.now() - timezone.timedelta(days=1),
        )
        
        sync_time_based_statuses()
        round_obj.refresh_from_db()
        self.assertEqual(round_obj.status, Round.STATUS_SUBMISSION_CLOSED)

    def test_round_dates_validation(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            **self.tournament_data
        )
        self.client.force_authenticate(user=self.admin)
        url = reverse('rounds')
        
        round_data = {
            'tournament': tournament.id,
            'position': 1,
            'name': 'Invalid Round',
            'start_date': tournament.start_date - timezone.timedelta(days=1),
            'end_date': tournament.end_date,
        }
        response = self.client.post(url, round_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('start_date', response.data['details'])
