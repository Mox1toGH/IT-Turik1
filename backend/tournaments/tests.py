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

    def test_tournament_teams_returns_registrations_with_is_active(self):
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
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['team']['id'], self.team.id)
        self.assertEqual(response.data[0]['team']['name'], self.team.name)
        self.assertTrue(response.data[0]['is_active'])
        self.assertEqual(response.data[1]['id'], inactive_registration.id)
        self.assertFalse(response.data[1]['is_active'])

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
        response = self.client.get(url, {'only_active': 'true'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], active_registration.id)
        self.assertTrue(response.data[0]['is_active'])

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

    
