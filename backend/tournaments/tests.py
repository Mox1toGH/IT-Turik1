from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from evaluation.models import JuryAssignment
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
        self.jury = User.objects.create_user(
            username='jury',
            email='jury@example.com',
            password='StrongPass123!',
            role='jury',
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
        }

    def test_admin_can_create_tournament(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('tournament_manage_create')
        response = self.client.post(url, self.tournament_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tournament.objects.count(), 1)
        self.assertEqual(Round.objects.count(), 0)

    def test_organizer_can_create_tournament(self):
        url = reverse('tournament_manage_create')

        self.client.force_authenticate(user=self.organizer)
        response = self.client.post(url, self.tournament_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_jury_cannot_create_tournament(self):
        self.client.force_authenticate(user=self.jury)
        url = reverse('tournament_manage_create')
        response = self.client.post(url, self.tournament_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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

    def test_organizer_can_update_tournament(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            **self.tournament_data
        )
        self.client.force_authenticate(user=self.organizer)
        url = reverse('tournament_manage_update', kwargs={'pk': tournament.id})
        response = self.client.patch(url, {'name': 'Updated by organizer'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_jury_cannot_update_tournament(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            **self.tournament_data
        )
        self.client.force_authenticate(user=self.jury)
        url = reverse('tournament_manage_update', kwargs={'pk': tournament.id})
        response = self.client.patch(url, {'name': 'Updated by jury'}, format='json')

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

    def test_jury_cannot_start_registration(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            **self.tournament_data
        )
        self.client.force_authenticate(user=self.jury)
        url = reverse('tournament_start_registration', kwargs={'pk': tournament.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        tournament.refresh_from_db()
        self.assertEqual(tournament.status, Tournament.STATUS_DRAFT)

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

    def test_admin_cannot_register_team(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_REGISTRATION,
            **self.tournament_data
        )
        self.client.force_authenticate(user=self.admin)
        url = reverse('tournament_register_team', kwargs={'pk': tournament.id})
        response = self.client.post(url, {'team_id': self.team.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(TournamentTeamRegistration.objects.filter(tournament=tournament, team=self.team).exists())

    def test_captain_can_leave_team_from_tournament(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_REGISTRATION,
            **self.tournament_data
        )
        registration = TournamentTeamRegistration.objects.create(
            tournament=tournament,
            team=self.team,
            created_by=self.captain,
            is_active=True,
        )

        self.client.force_authenticate(user=self.captain)
        url = reverse('tournament_leave_team', kwargs={'pk': tournament.id})
        response = self.client.post(url, {'team_id': self.team.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        registration.refresh_from_db()
        self.assertFalse(registration.is_active)

    def test_non_captain_cannot_leave_team_from_tournament(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_REGISTRATION,
            **self.tournament_data
        )
        registration = TournamentTeamRegistration.objects.create(
            tournament=tournament,
            team=self.team,
            created_by=self.captain,
            is_active=True,
        )
        member = User.objects.create_user(
            username='member-leave',
            email='member-leave@example.com',
            password='StrongPass123!',
        )
        TeamMember.objects.create(team=self.team, user=member)

        self.client.force_authenticate(user=member)
        url = reverse('tournament_leave_team', kwargs={'pk': tournament.id})
        response = self.client.post(url, {'team_id': self.team.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        registration.refresh_from_db()
        self.assertTrue(registration.is_active)

    def test_team_can_reregister_same_tournament_after_leave(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_REGISTRATION,
            **self.tournament_data
        )
        registration = TournamentTeamRegistration.objects.create(
            tournament=tournament,
            team=self.team,
            created_by=self.captain,
            is_active=False,
        )

        self.client.force_authenticate(user=self.captain)
        url = reverse('tournament_register_team', kwargs={'pk': tournament.id})
        response = self.client.post(url, {'team_id': self.team.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        registration.refresh_from_db()
        self.assertTrue(registration.is_active)
        self.assertEqual(
            TournamentTeamRegistration.objects.filter(tournament=tournament, team=self.team).count(),
            1,
        )

    def test_round_management(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            **self.tournament_data
        )
        self.client.force_authenticate(user=self.admin)
        url = reverse('rounds', kwargs={'tournament_pk': tournament.id})
        
        round_data = {
            'name': 'Extra Round',
            'start_date': self.tournament_data['start_date'],
            'end_date': self.tournament_data['end_date'],
        }
        response = self.client.post(url, round_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_organizer_can_manage_rounds(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            **self.tournament_data
        )
        self.client.force_authenticate(user=self.organizer)
        url = reverse('rounds', kwargs={'tournament_pk': tournament.id})

        round_data = {
            'name': 'Organizer Round',
            'start_date': self.tournament_data['start_date'],
            'end_date': self.tournament_data['end_date'],
        }
        response = self.client.post(url, round_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_jury_cannot_manage_rounds(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            **self.tournament_data
        )
        self.client.force_authenticate(user=self.jury)
        url = reverse('rounds', kwargs={'tournament_pk': tournament.id})

        round_data = {
            'name': 'Jury Round',
            'start_date': self.tournament_data['start_date'],
            'end_date': self.tournament_data['end_date'],
        }
        response = self.client.post(url, round_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_submission_creation(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_RUNNING,
            **self.tournament_data
        )
        round_obj = Round.objects.create(
            tournament=tournament,
            status=Round.STATUS_ACTIVE,
            start_date=timezone.now() - timezone.timedelta(hours=1),
            end_date=timezone.now() + timezone.timedelta(hours=1),
        )
        TournamentTeamRegistration.objects.create(tournament=tournament, team=self.team)
        
        self.client.force_authenticate(user=self.captain)
        url = reverse('submissions')
        submission_data = {
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
            status=Round.STATUS_ACTIVE,
            start_date=timezone.now() - timezone.timedelta(hours=1),
            end_date=timezone.now() + timezone.timedelta(hours=1),
        )

        self.client.force_authenticate(user=self.captain)
        url = reverse('submissions')
        submission_data = {
            'round': round_obj.id,
            'github_url': 'https://github.com/test/repo',
            'demo_video_url': 'https://youtube.com/test',
            'description': 'Unregistered team submission',
        }
        response = self.client.post(url, submission_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('code'), 'validation_error')
        self.assertIn('team', response.data['details'])

    def test_non_captain_team_member_cannot_create_submission(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_RUNNING,
            **self.tournament_data
        )
        round_obj = Round.objects.create(
            tournament=tournament,
            status=Round.STATUS_ACTIVE,
            start_date=timezone.now() - timezone.timedelta(hours=1),
            end_date=timezone.now() + timezone.timedelta(hours=1),
        )
        TournamentTeamRegistration.objects.create(tournament=tournament, team=self.team)

        member = User.objects.create_user(
            username='member-create',
            email='member-create@example.com',
            password='StrongPass123!',
        )
        TeamMember.objects.create(team=self.team, user=member)

        self.client.force_authenticate(user=member)
        url = reverse('submissions')
        submission_data = {
            'round': round_obj.id,
            'github_url': 'https://github.com/test/repo',
            'demo_video_url': 'https://youtube.com/test',
            'description': 'Member submission',
        }
        response = self.client.post(url, submission_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('code'), 'validation_error')
        self.assertIn('team', response.data['details'])

    def test_non_captain_team_member_cannot_update_submission(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_RUNNING,
            **self.tournament_data
        )
        round_obj = Round.objects.create(
            tournament=tournament,
            status=Round.STATUS_ACTIVE,
            start_date=timezone.now() - timezone.timedelta(hours=1),
            end_date=timezone.now() + timezone.timedelta(hours=1),
        )
        TournamentTeamRegistration.objects.create(tournament=tournament, team=self.team)
        submission = Submission.objects.create(
            team=self.team,
            round=round_obj,
            github_url='https://github.com/test/repo',
            demo_video_url='https://youtube.com/test',
            description='Captain submission',
            created_by=self.captain,
        )

        member = User.objects.create_user(
            username='member-update',
            email='member-update@example.com',
            password='StrongPass123!',
        )
        TeamMember.objects.create(team=self.team, user=member)

        self.client.force_authenticate(user=member)
        url = reverse('submission_detail', kwargs={'pk': submission.id})
        response = self.client.patch(url, {'description': 'Updated by member'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('code'), 'validation_error')
        self.assertIn('team', response.data['details'])

    def test_captain_can_update_submission(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_RUNNING,
            **self.tournament_data
        )
        round_obj = Round.objects.create(
            tournament=tournament,
            status=Round.STATUS_ACTIVE,
            start_date=timezone.now() - timezone.timedelta(hours=1),
            end_date=timezone.now() + timezone.timedelta(hours=1),
        )
        TournamentTeamRegistration.objects.create(tournament=tournament, team=self.team)
        submission = Submission.objects.create(
            team=self.team,
            round=round_obj,
            github_url='https://github.com/test/repo',
            demo_video_url='https://youtube.com/test',
            description='Captain submission',
            created_by=self.captain,
        )

        self.client.force_authenticate(user=self.captain)
        url = reverse('submission_detail', kwargs={'pk': submission.id})
        response = self.client.patch(url, {'description': 'Updated by captain'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        submission.refresh_from_db()
        self.assertEqual(submission.description, 'Updated by captain')

    def test_tournament_submissions_returns_all_teams_submissions(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_RUNNING,
            **self.tournament_data
        )
        round_obj = Round.objects.create(
            tournament=tournament,
            status=Round.STATUS_ACTIVE,
            start_date=timezone.now() - timezone.timedelta(hours=1),
            end_date=timezone.now() + timezone.timedelta(hours=1),
        )
        TournamentTeamRegistration.objects.create(tournament=tournament, team=self.team)
        own_submission = Submission.objects.create(
            team=self.team,
            round=round_obj,
            github_url='https://github.com/test/my-team',
            demo_video_url='https://youtube.com/my-team',
            created_by=self.captain,
        )

        other_captain = User.objects.create_user(
            username='captain-other',
            email='captain-other@example.com',
            password='StrongPass123!',
        )
        other_team = Team.objects.create(
            name='Other Team',
            email='other-team@example.com',
            captain=other_captain,
        )
        TeamMember.objects.create(team=other_team, user=other_captain)
        TournamentTeamRegistration.objects.create(tournament=tournament, team=other_team)
        Submission.objects.create(
            team=other_team,
            round=round_obj,
            github_url='https://github.com/test/other-team',
            demo_video_url='https://youtube.com/other-team',
            created_by=other_captain,
        )

        self.client.force_authenticate(user=self.captain)
        url = reverse('tournament_submissions', kwargs={'pk': tournament.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        returned_ids = {item['id'] for item in response.data}
        self.assertIn(own_submission.id, returned_ids)

    def test_tournament_submissions_does_not_include_other_tournament_submissions(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_RUNNING,
            **self.tournament_data
        )
        other_tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_RUNNING,
            name='Other tournament',
            description='Other tournament desc',
            start_date=timezone.now() + timezone.timedelta(days=2),
            end_date=timezone.now() + timezone.timedelta(days=12),
        )
        round_obj = Round.objects.create(
            tournament=tournament,
            status=Round.STATUS_ACTIVE,
            start_date=timezone.now() - timezone.timedelta(hours=1),
            end_date=timezone.now() + timezone.timedelta(hours=1),
        )
        other_round = Round.objects.create(
            tournament=other_tournament,
            status=Round.STATUS_ACTIVE,
            start_date=timezone.now() - timezone.timedelta(hours=1),
            end_date=timezone.now() + timezone.timedelta(hours=1),
        )
        TournamentTeamRegistration.objects.create(tournament=tournament, team=self.team)
        TournamentTeamRegistration.objects.create(tournament=other_tournament, team=self.team)
        own_submission = Submission.objects.create(
            team=self.team,
            round=round_obj,
            github_url='https://github.com/test/current-tournament',
            demo_video_url='https://youtube.com/current-tournament',
            created_by=self.captain,
        )
        Submission.objects.create(
            team=self.team,
            round=other_round,
            github_url='https://github.com/test/other-tournament',
            demo_video_url='https://youtube.com/other-tournament',
            created_by=self.captain,
        )

        self.client.force_authenticate(user=self.captain)
        url = reverse('tournament_submissions', kwargs={'pk': tournament.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], own_submission.id)

    def test_tournament_my_submissions_returns_only_captain_team_submissions(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_RUNNING,
            **self.tournament_data
        )
        round_obj = Round.objects.create(
            tournament=tournament,
            status=Round.STATUS_ACTIVE,
            start_date=timezone.now() - timezone.timedelta(hours=1),
            end_date=timezone.now() + timezone.timedelta(hours=1),
        )
        TournamentTeamRegistration.objects.create(tournament=tournament, team=self.team)
        own_submission = Submission.objects.create(
            team=self.team,
            round=round_obj,
            github_url='https://github.com/test/repo',
            demo_video_url='https://youtube.com/test',
            created_by=self.captain,
        )

        other_captain = User.objects.create_user(
            username='captain-other-2',
            email='captain-other-2@example.com',
            password='StrongPass123!',
        )
        other_team = Team.objects.create(
            name='Other Team 2',
            email='other-team-2@example.com',
            captain=other_captain,
        )
        TeamMember.objects.create(team=other_team, user=other_captain)
        TournamentTeamRegistration.objects.create(tournament=tournament, team=other_team, is_active=True)
        Submission.objects.create(
            team=other_team,
            round=round_obj,
            github_url='https://github.com/test/other-repo',
            demo_video_url='https://youtube.com/other-test',
            created_by=other_captain,
        )

        self.client.force_authenticate(user=self.captain)
        url = reverse('tournament_my_submissions', kwargs={'pk': tournament.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], own_submission.id)

    def test_tournament_my_submissions_returns_member_team_submissions(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_RUNNING,
            **self.tournament_data
        )
        round_obj = Round.objects.create(
            tournament=tournament,
            status=Round.STATUS_ACTIVE,
            start_date=timezone.now() - timezone.timedelta(hours=1),
            end_date=timezone.now() + timezone.timedelta(hours=1),
        )
        member = User.objects.create_user(
            username='member-my-team',
            email='member-my-team@example.com',
            password='StrongPass123!',
        )
        TeamMember.objects.create(team=self.team, user=member)
        TournamentTeamRegistration.objects.create(tournament=tournament, team=self.team, is_active=True)
        own_submission = Submission.objects.create(
            team=self.team,
            round=round_obj,
            github_url='https://github.com/test/member-repo',
            demo_video_url='https://youtube.com/member-test',
            created_by=self.captain,
        )

        self.client.force_authenticate(user=member)
        url = reverse('tournament_my_submissions', kwargs={'pk': tournament.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], own_submission.id)

    def test_tournament_my_submissions_does_not_include_other_tournament_submissions(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_RUNNING,
            **self.tournament_data
        )
        other_tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_RUNNING,
            name='Other tournament for my submissions',
            description='Other tournament desc',
            start_date=timezone.now() + timezone.timedelta(days=2),
            end_date=timezone.now() + timezone.timedelta(days=12),
        )
        round_obj = Round.objects.create(
            tournament=tournament,
            status=Round.STATUS_ACTIVE,
            start_date=timezone.now() - timezone.timedelta(hours=1),
            end_date=timezone.now() + timezone.timedelta(hours=1),
        )
        other_round = Round.objects.create(
            tournament=other_tournament,
            status=Round.STATUS_ACTIVE,
            start_date=timezone.now() - timezone.timedelta(hours=1),
            end_date=timezone.now() + timezone.timedelta(hours=1),
        )
        TournamentTeamRegistration.objects.create(tournament=tournament, team=self.team, is_active=True)
        TournamentTeamRegistration.objects.create(tournament=other_tournament, team=self.team, is_active=True)
        own_submission = Submission.objects.create(
            team=self.team,
            round=round_obj,
            github_url='https://github.com/test/current-tournament-my',
            demo_video_url='https://youtube.com/current-tournament-my',
            created_by=self.captain,
        )
        Submission.objects.create(
            team=self.team,
            round=other_round,
            github_url='https://github.com/test/other-tournament-my',
            demo_video_url='https://youtube.com/other-tournament-my',
            created_by=self.captain,
        )

        self.client.force_authenticate(user=self.captain)
        url = reverse('tournament_my_submissions', kwargs={'pk': tournament.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], own_submission.id)

    def test_tournament_my_submissions_returns_404_when_user_not_participating(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_RUNNING,
            **self.tournament_data
        )
        outsider = User.objects.create_user(
            username='outsider',
            email='outsider@example.com',
            password='StrongPass123!',
        )
        self.client.force_authenticate(user=outsider)
        url = reverse('tournament_my_submissions', kwargs={'pk': tournament.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_tournament_my_submissions_requires_authentication(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_RUNNING,
            **self.tournament_data
        )
        url = reverse('tournament_my_submissions', kwargs={'pk': tournament.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_tournament_my_submissions_returns_404_for_missing_tournament(self):
        self.client.force_authenticate(user=self.captain)
        url = reverse('tournament_my_submissions', kwargs={'pk': 999999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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

    def test_registration_fails_when_team_already_in_another_active_tournament(self):
        active_tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_REGISTRATION,
            **self.tournament_data
        )
        TournamentTeamRegistration.objects.create(
            tournament=active_tournament,
            team=self.team,
            created_by=self.captain,
        )

        target_tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_REGISTRATION,
            **self.tournament_data
        )

        self.client.force_authenticate(user=self.captain)
        url = reverse('tournament_register_team', kwargs={'pk': target_tournament.id})
        response = self.client.post(url, {'team_id': self.team.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['details'].get('team'),
            'This team is already participating in another tournament.',
        )

    def test_registration_fails_when_team_shares_members_with_active_tournament_team(self):
        shared_user = User.objects.create_user(
            username='shared-member',
            email='shared-member@example.com',
            password='StrongPass123!',
        )
        TeamMember.objects.create(team=self.team, user=shared_user)

        other_captain = User.objects.create_user(
            username='other-captain',
            email='other-captain@example.com',
            password='StrongPass123!',
        )
        other_team = Team.objects.create(
            name='Other Team',
            email='other-team@example.com',
            captain=other_captain,
        )
        TeamMember.objects.create(team=other_team, user=other_captain)
        TeamMember.objects.create(team=other_team, user=shared_user)

        active_tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_REGISTRATION,
            **self.tournament_data
        )
        TournamentTeamRegistration.objects.create(
            tournament=active_tournament,
            team=other_team,
            created_by=other_captain,
        )

        target_tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_REGISTRATION,
            **self.tournament_data
        )

        self.client.force_authenticate(user=self.captain)
        url = reverse('tournament_register_team', kwargs={'pk': target_tournament.id})
        response = self.client.post(url, {'team_id': self.team.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('team', response.data['details'])
        self.assertIn(shared_user.email, response.data['details']['team'])

    def test_inactive_registration_does_not_block_reregistration(self):
        """
        A team with is_active=False registration must be allowed to register
        for another tournament without hitting 'already participating'.
        """
        old_tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_REGISTRATION,
            **self.tournament_data
        )
        TournamentTeamRegistration.objects.create(
            tournament=old_tournament,
            team=self.team,
            created_by=self.captain,
            is_active=False,
        )

        new_tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_REGISTRATION,
            **self.tournament_data
        )

        self.client.force_authenticate(user=self.captain)
        url = reverse('tournament_register_team', kwargs={'pk': new_tournament.id})
        response = self.client.post(url, {'team_id': self.team.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_inactive_registration_does_not_cause_shared_member_conflict(self):
        """
        Shared member between two teams must NOT trigger a conflict error
        if the first team's registration is inactive (is_active=False).
        """
        shared_user = User.objects.create_user(
            username='shared-member2',
            email='shared-member2@example.com',
            password='StrongPass123!',
        )
        TeamMember.objects.create(team=self.team, user=shared_user)

        other_captain = User.objects.create_user(
            username='other-captain2',
            email='other-captain2@example.com',
            password='StrongPass123!',
        )
        other_team = Team.objects.create(
            name='Other Team 2',
            email='other-team2@example.com',
            captain=other_captain,
        )
        TeamMember.objects.create(team=other_team, user=shared_user)

        old_tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_RUNNING,
            **self.tournament_data
        )
        TournamentTeamRegistration.objects.create(
            tournament=old_tournament,
            team=self.team,
            created_by=self.captain,
            is_active=False,  # deactivated; must not count as conflict
        )

        new_tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_REGISTRATION,
            **self.tournament_data
        )

        self.client.force_authenticate(user=other_captain)
        url = reverse('tournament_register_team', kwargs={'pk': new_tournament.id})
        response = self.client.post(url, {'team_id': other_team.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_eligible_teams_returns_only_captain_teams_with_members_count(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_REGISTRATION,
            **self.tournament_data
        )
        other_captain = User.objects.create_user(
            username='another-captain',
            email='another-captain@example.com',
            password='StrongPass123!',
        )
        other_team = Team.objects.create(
            name='Other Captain Team',
            email='other-captain-team@example.com',
            captain=other_captain,
        )
        TeamMember.objects.create(team=other_team, user=other_captain)

        extra_member = User.objects.create_user(
            username='extra-member',
            email='extra-member@example.com',
            password='StrongPass123!',
        )
        TeamMember.objects.create(team=self.team, user=extra_member)

        self.client.force_authenticate(user=self.captain)
        url = reverse('tournament_eligible_teams', kwargs={'pk': tournament.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.team.id)
        self.assertEqual(response.data[0]['name'], self.team.name)
        self.assertEqual(response.data[0]['members_count'], 3)

    def test_team_active_tournament_returns_registration_or_running_tournament(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_REGISTRATION,
            **self.tournament_data
        )
        TournamentTeamRegistration.objects.create(
            tournament=tournament,
            team=self.team,
            created_by=self.captain,
        )

        self.client.force_authenticate(user=self.captain)
        url = reverse('team_active_tournament')
        response = self.client.get(url, {'team_id': self.team.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], tournament.id)
        self.assertEqual(response.data['name'], tournament.name)
        self.assertEqual(response.data['status'], tournament.status)
        self.assertIn('start_date', response.data)

    def test_team_active_tournament_returns_404_when_not_found(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_FINISHED,
            **self.tournament_data
        )
        TournamentTeamRegistration.objects.create(
            tournament=tournament,
            team=self.team,
            created_by=self.captain,
        )

        self.client.force_authenticate(user=self.captain)
        url = reverse('team_active_tournament')
        response = self.client.get(url, {'team_id': self.team.id})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_tournament_teams_returns_only_active_by_default(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_RUNNING,
            **self.tournament_data
        )
        second_user = User.objects.create_user(
            username='second-captain',
            email='second-captain@example.com',
            password='StrongPass123!',
        )
        second_team = Team.objects.create(
            name='Second Team',
            email='second-team@example.com',
            captain=second_user,
        )
        TeamMember.objects.create(team=second_team, user=second_user)

        TournamentTeamRegistration.objects.create(
            tournament=tournament,
            team=self.team,
            created_by=self.captain,
            is_active=True,
        )
        inactive_registration = TournamentTeamRegistration.objects.create(
            tournament=tournament,
            team=second_team,
            created_by=second_user,
            is_active=False,
        )

        self.client.force_authenticate(user=self.captain)
        url = reverse('tournament_teams', kwargs={'pk': tournament.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.team.id)
        self.assertEqual(response.data[0]['name'], self.team.name)
        self.assertTrue(response.data[0]['is_active'])

    def test_tournament_teams_can_include_inactive(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_RUNNING,
            **self.tournament_data
        )
        second_user = User.objects.create_user(
            username='second-captain-include',
            email='second-captain-include@example.com',
            password='StrongPass123!',
        )
        second_team = Team.objects.create(
            name='Second Team Include',
            email='second-team-include@example.com',
            captain=second_user,
        )
        TeamMember.objects.create(team=second_team, user=second_user)

        TournamentTeamRegistration.objects.create(
            tournament=tournament,
            team=self.team,
            created_by=self.captain,
            is_active=True,
        )
        TournamentTeamRegistration.objects.create(
            tournament=tournament,
            team=second_team,
            created_by=second_user,
            is_active=False,
        )

        self.client.force_authenticate(user=self.captain)
        url = reverse('tournament_teams', kwargs={'pk': tournament.id})
        response = self.client.get(url, {'include_inactive': 'true'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertTrue(any(item['is_active'] for item in response.data))
        self.assertTrue(any(not item['is_active'] for item in response.data))

    def test_tournament_teams_filters_only_active(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_RUNNING,
            **self.tournament_data
        )
        second_user = User.objects.create_user(
            username='third-captain',
            email='third-captain@example.com',
            password='StrongPass123!',
        )
        second_team = Team.objects.create(
            name='Third Team',
            email='third-team@example.com',
            captain=second_user,
        )
        TeamMember.objects.create(team=second_team, user=second_user)

        active_registration = TournamentTeamRegistration.objects.create(
            tournament=tournament,
            team=self.team,
            created_by=self.captain,
            is_active=True,
        )
        TournamentTeamRegistration.objects.create(
            tournament=tournament,
            team=second_team,
            created_by=second_user,
            is_active=False,
        )

        self.client.force_authenticate(user=self.captain)
        url = reverse('tournament_teams', kwargs={'pk': tournament.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], active_registration.team_id)
        self.assertTrue(response.data[0]['is_active'])

    def test_team_active_tournament_ignores_inactive_registration(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_REGISTRATION,
            **self.tournament_data
        )
        TournamentTeamRegistration.objects.create(
            tournament=tournament,
            team=self.team,
            created_by=self.captain,
            is_active=False,
        )

        self.client.force_authenticate(user=self.captain)
        url = reverse('team_active_tournament')
        response = self.client.get(url, {'team_id': self.team.id})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_tournament_teams_returns_404_for_missing_tournament(self):
        self.client.force_authenticate(user=self.captain)
        url = reverse('tournament_teams', kwargs={'pk': 999999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_tournament_teams_requires_authentication(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_RUNNING,
            **self.tournament_data
        )
        url = reverse('tournament_teams', kwargs={'pk': tournament.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_sync_time_based_statuses(self):
        from .services import sync_time_based_statuses
        
        tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_RUNNING,
            **self.tournament_data
        )
        round_obj = Round.objects.create(
            tournament=tournament,
            status=Round.STATUS_ACTIVE,
            start_date=timezone.now() - timezone.timedelta(days=2),
            end_date=timezone.now() - timezone.timedelta(days=1),
        )
        
        sync_time_based_statuses()
        round_obj.refresh_from_db()
        self.assertEqual(round_obj.status, Round.STATUS_SUBMISSION_CLOSED)

    def test_tournament_list_pagination_response_shape(self):
        Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_REGISTRATION,
            **self.tournament_data
        )
        url = reverse('tournaments')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
        self.assertIn('total', response.data)
        self.assertIsInstance(response.data['data'], list)
        self.assertIsInstance(response.data['total'], int)

    def test_tournament_list_pagination_page_size(self):
        for i in range(25):
            Tournament.objects.create(
                created_by=self.admin,
                status=Tournament.STATUS_REGISTRATION,
                name=f'Tournament {i}',
                description=f'Desc {i}',
                start_date=timezone.now() + timezone.timedelta(days=1),
                end_date=timezone.now() + timezone.timedelta(days=10),
            )

        url = reverse('tournaments')
        response = self.client.get(url, {'page': '1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 25)
        self.assertEqual(len(response.data['data']), 20)

        response2 = self.client.get(url, {'page': '2'})
        self.assertEqual(len(response2.data['data']), 5)

    def test_tournament_list_pagination_custom_page_size(self):
        for i in range(15):
            Tournament.objects.create(
                created_by=self.admin,
                status=Tournament.STATUS_REGISTRATION,
                name=f'Tournament {i}',
                description=f'Desc {i}',
                start_date=timezone.now() + timezone.timedelta(days=1),
                end_date=timezone.now() + timezone.timedelta(days=10),
            )

        url = reverse('tournaments')
        response = self.client.get(url, {'page': '1', 'pageSize': '5'})
        self.assertEqual(response.data['total'], 15)
        self.assertEqual(len(response.data['data']), 5)

        response2 = self.client.get(url, {'page': '3', 'pageSize': '5'})
        self.assertEqual(len(response2.data['data']), 5)

    def test_tournament_list_pagination_max_page_size(self):
        for i in range(150):
            Tournament.objects.create(
                created_by=self.admin,
                status=Tournament.STATUS_REGISTRATION,
                name=f'Tournament {i}',
                description=f'Desc {i}',
                start_date=timezone.now() + timezone.timedelta(days=1),
                end_date=timezone.now() + timezone.timedelta(days=10),
            )

        url = reverse('tournaments')
        response = self.client.get(url, {'page': '1', 'pageSize': '9999'})
        self.assertEqual(response.data['total'], 150)
        self.assertEqual(len(response.data['data']), 100)

    def test_tournament_list_pagination_default_page(self):
        Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_REGISTRATION,
            **self.tournament_data
        )
        url = reverse('tournaments')
        response = self.client.get(url)
        self.assertEqual(response.data['total'], 1)
        self.assertEqual(len(response.data['data']), 1)

    def test_tournament_list_filter_by_search_query(self):
        Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_REGISTRATION,
            name='Alpha Cup',
            description='First tournament',
            start_date=timezone.now() + timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=10),
        )
        Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_REGISTRATION,
            name='Beta Cup',
            description='Second tournament',
            start_date=timezone.now() + timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=10),
        )
        url = reverse('tournaments')
        response = self.client.get(url, {'searchQuery': 'Alpha'})
        self.assertEqual(response.data['total'], 1)
        self.assertEqual(response.data['data'][0]['name'], 'Alpha Cup')

    def test_tournament_list_filter_by_search_query_description(self):
        Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_REGISTRATION,
            name='Alpha Cup',
            description='Unique keyword here',
            start_date=timezone.now() + timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=10),
        )
        Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_REGISTRATION,
            name='Beta Cup',
            description='Other description',
            start_date=timezone.now() + timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=10),
        )
        url = reverse('tournaments')
        response = self.client.get(url, {'searchQuery': 'Unique keyword'})
        self.assertEqual(response.data['total'], 1)
        self.assertEqual(response.data['data'][0]['name'], 'Alpha Cup')

    def test_tournament_list_filter_by_status(self):
        Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_REGISTRATION,
            name='Reg Tournament',
            description='desc',
            start_date=timezone.now() + timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=10),
        )
        Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_RUNNING,
            name='Running Tournament',
            description='desc',
            start_date=timezone.now() + timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=10),
        )
        url = reverse('tournaments')
        response = self.client.get(url, {'status': 'registration'})
        self.assertEqual(response.data['total'], 1)
        self.assertEqual(response.data['data'][0]['name'], 'Reg Tournament')

    def test_tournament_list_filter_by_multiple_statuses(self):
        reg_tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_REGISTRATION,
            name='Reg Tournament',
            description='desc',
            start_date=timezone.now() + timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=10),
        )
        running_tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_RUNNING,
            name='Running Tournament',
            description='desc',
            start_date=timezone.now() + timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=10),
        )
        Round.objects.create(
            tournament=running_tournament,
            status=Round.STATUS_ACTIVE,
            start_date=timezone.now() - timezone.timedelta(hours=1),
            end_date=timezone.now() + timezone.timedelta(days=5),
        )
        Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_FINISHED,
            name='Finished Tournament',
            description='desc',
            start_date=timezone.now() + timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=10),
        )
        url = reverse('tournaments')
        response = self.client.get(url, {'status': 'registration,running'})
        self.assertEqual(response.data['total'], 2)

    def test_tournament_list_filter_by_start_at(self):
        today = timezone.now().date()
        Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_REGISTRATION,
            name='Today Start',
            description='desc',
            start_date=timezone.now().replace(hour=10, minute=0, second=0),
            end_date=timezone.now() + timezone.timedelta(days=10),
        )
        Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_REGISTRATION,
            name='Tomorrow Start',
            description='desc',
            start_date=timezone.now() + timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=10),
        )
        url = reverse('tournaments')
        response = self.client.get(url, {'startAt': today.isoformat()})
        self.assertEqual(response.data['total'], 1)
        self.assertEqual(response.data['data'][0]['name'], 'Today Start')

    def test_tournament_list_hides_draft_for_anonymous(self):
        Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_DRAFT,
            name='Draft Tournament',
            description='desc',
            start_date=timezone.now() + timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=10),
        )
        Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_REGISTRATION,
            name='Public Tournament',
            description='desc',
            start_date=timezone.now() + timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=10),
        )
        url = reverse('tournaments')
        response = self.client.get(url)
        self.assertEqual(response.data['total'], 1)
        self.assertEqual(response.data['data'][0]['name'], 'Public Tournament')

    def test_tournament_list_shows_draft_to_admin(self):
        Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_DRAFT,
            name='Draft Tournament',
            description='desc',
            start_date=timezone.now() + timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=10),
        )
        self.client.force_authenticate(user=self.admin)
        url = reverse('tournaments')
        response = self.client.get(url)
        self.assertEqual(response.data['total'], 1)
        self.assertEqual(response.data['data'][0]['name'], 'Draft Tournament')

    def test_round_dates_validation(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            **self.tournament_data
        )
        self.client.force_authenticate(user=self.admin)
        url = reverse('rounds', kwargs={'tournament_pk': tournament.id})
        
        round_data = {
            'name': 'Invalid Round',
            'start_date': tournament.start_date - timezone.timedelta(days=1),
            'end_date': tournament.end_date,
        }
        response = self.client.post(url, round_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('start_date', response.data['details'])

    def test_round_date_overlap_validation(self):
        """Test that rounds cannot have overlapping dates within the same tournament"""
        tournament = Tournament.objects.create(
            created_by=self.admin,
            **self.tournament_data
        )
        
        # Create first round directly with model (bypasses single-round validation)
        round1 = Round.objects.create(
            tournament=tournament,
            name='Round 1',
            start_date=tournament.start_date,
            end_date=tournament.start_date + timezone.timedelta(days=3),
        )
        
        self.client.force_authenticate(user=self.admin)
        url = reverse('rounds', kwargs={'tournament_pk': tournament.id})
        
        # Try to create overlapping round via API (starts during first round)
        round2_data = {
            'name': 'Round 2',
            'start_date': (tournament.start_date + timezone.timedelta(days=2)).isoformat(),
            'end_date': (tournament.start_date + timezone.timedelta(days=5)).isoformat(),
        }
        response = self.client.post(url, round2_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('start_date', response.data['details'])
        self.assertIn('overlap', response.data['details']['start_date'][0].lower())
        
        # Try to create round that ends during first round
        round3_data = {
            'name': 'Round 3',
            'start_date': (tournament.start_date - timezone.timedelta(days=1)).isoformat(),
            'end_date': (tournament.start_date + timezone.timedelta(days=1)).isoformat(),
        }
        response = self.client.post(url, round3_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('start_date', response.data['details'])
        
        # For single-round tournaments this still fails due to round date constraints
        round4_data = {
            'name': 'Round 4',
            'start_date': (tournament.start_date + timezone.timedelta(days=4)).isoformat(),
            'end_date': (tournament.start_date + timezone.timedelta(days=6)).isoformat(),
        }
        response = self.client.post(url, round4_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('start_date', response.data['details'])

    def test_round_date_overlap_update_validation(self):
        """Test that updating a round cannot cause date overlaps"""
        tournament = Tournament.objects.create(
            created_by=self.admin,
            **self.tournament_data
        )
        
        # Create two non-overlapping rounds
        round1 = Round.objects.create(
            tournament=tournament,
            name='Round 1',
            start_date=tournament.start_date,
            end_date=tournament.start_date + timezone.timedelta(days=2),
        )
        round2 = Round.objects.create(
            tournament=tournament,
            name='Round 2',
            start_date=tournament.start_date + timezone.timedelta(days=3),
            end_date=tournament.start_date + timezone.timedelta(days=5),
        )
        
        self.client.force_authenticate(user=self.admin)
        url = reverse('round_detail', kwargs={'pk': round2.id})
        
        # Try to update round2 to overlap with round1
        update_data = {
            'tournament': tournament.id,
            'name': 'Round 2 Updated',
            'start_date': (tournament.start_date + timezone.timedelta(days=1)).isoformat(),
            'end_date': (tournament.start_date + timezone.timedelta(days=4)).isoformat(),
        }
        response = self.client.put(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('start_date', response.data['details'])
        self.assertIn('overlap', response.data['details']['start_date'][0].lower())

    def test_round_date_overlap_when_first_round_extended_into_second(self):
        """Test that first round cannot be updated to end inside second round."""
        tournament = Tournament.objects.create(
            created_by=self.admin,
            **self.tournament_data
        )

        round1 = Round.objects.create(
            tournament=tournament,
            name='Round 1',
            start_date=tournament.start_date,
            end_date=tournament.start_date + timezone.timedelta(days=2),
        )
        Round.objects.create(
            tournament=tournament,
            name='Round 2',
            start_date=tournament.start_date + timezone.timedelta(days=3),
            end_date=tournament.start_date + timezone.timedelta(days=6),
        )

        self.client.force_authenticate(user=self.admin)
        url = reverse('round_detail', kwargs={'pk': round1.id})
        update_data = {
            'tournament': tournament.id,
            'name': 'Round 1',
            'start_date': tournament.start_date.isoformat(),
            'end_date': (tournament.start_date + timezone.timedelta(days=4)).isoformat(),
        }

        response = self.client.put(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('start_date', response.data['details'])
        self.assertIn('overlap', response.data['details']['start_date'][0].lower())

    def test_round_date_overlap_update_validation(self):
        """Test that updating a round cannot cause date overlaps"""
        tournament = Tournament.objects.create(
            created_by=self.admin,
            **self.tournament_data
        )
        
        # Create two non-overlapping rounds
        round1 = Round.objects.create(
            tournament=tournament,
            name='Round 1',
            start_date=tournament.start_date,
            end_date=tournament.start_date + timezone.timedelta(hours=2),
        )
        round2 = Round.objects.create(
            tournament=tournament,
            name='Round 2',
            start_date=tournament.start_date + timezone.timedelta(hours=3),
            end_date=tournament.start_date + timezone.timedelta(hours=5),
        )
        
        self.client.force_authenticate(user=self.admin)
        url = reverse('round_detail', kwargs={'pk': round2.id})
        
        # Try to update round2 to overlap with round1
        update_data = {
            'tournament': tournament.id,
            'name': 'Round 2 Updated',
            'start_date': tournament.start_date + timezone.timedelta(hours=1),
            'end_date': tournament.start_date + timezone.timedelta(hours=4),
        }
        response = self.client.put(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('start_date', response.data['details'])
        self.assertIn('overlap', response.data['details']['start_date'][0].lower())

    
class RoundSubmissionsAssignmentsTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin_round_subs',
            email='admin_round_subs@example.com',
            password='StrongPass123!',
            role='admin',
            is_staff=True,
            is_superuser=True,
        )
        self.captain = User.objects.create_user(
            username='captain_round_subs',
            email='captain_round_subs@example.com',
            password='StrongPass123!',
        )
        self.jury1 = User.objects.create_user(
            username='jury_round_subs_1',
            email='jury_round_subs_1@example.com',
            password='StrongPass123!',
            role='jury',
            full_name='Jury One',
        )
        self.jury2 = User.objects.create_user(
            username='jury_round_subs_2',
            email='jury_round_subs_2@example.com',
            password='StrongPass123!',
            role='jury',
            full_name='Jury Two',
        )

        self.tournament = Tournament.objects.create(
            name='Tournament Round Submissions',
            description='Round submissions with assignments',
            start_date=timezone.now() - timezone.timedelta(days=2),
            end_date=timezone.now() + timezone.timedelta(days=5),
            created_by=self.admin,
            status=Tournament.STATUS_RUNNING,
        )
        self.round_obj = Round.objects.create(
            tournament=self.tournament,
            name='Round A',
            start_date=timezone.now() - timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=1),
            status=Round.STATUS_ACTIVE,
        )
        self.team = Team.objects.create(
            name='Round Submissions Team',
            email='round_submissions_team@example.com',
            captain=self.captain,
        )
        TeamMember.objects.create(team=self.team, user=self.captain)
        TournamentTeamRegistration.objects.create(tournament=self.tournament, team=self.team, is_active=True)

        self.submission = Submission.objects.create(
            team=self.team,
            round=self.round_obj,
            github_url='https://github.com/example/repo',
            demo_video_url='https://example.com/demo',
            created_by=self.captain,
        )

    def test_round_submissions_includes_assignments(self):
        assign1 = JuryAssignment.objects.create(submission=self.submission, jury=self.jury1)
        assign2 = JuryAssignment.objects.create(submission=self.submission, jury=self.jury2)

        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse('round_submissions', kwargs={'pk': self.round_obj.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        assignments = response.data[0].get('assignments')
        self.assertIsInstance(assignments, list)
        returned_ids = {item['id'] for item in assignments}
        self.assertEqual(returned_ids, {assign1.id, assign2.id})

        jury_ids = {item['jury']['id'] for item in assignments}
        self.assertEqual(jury_ids, {self.jury1.id, self.jury2.id})
        self.assertTrue(all(item['jury']['role'] == 'jury' for item in assignments))
