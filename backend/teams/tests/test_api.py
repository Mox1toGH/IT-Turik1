from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User
from teams.models import Team, TeamInvitation, TeamJoinRequest, TeamMember
from tournaments.models import Tournament, TournamentTeamRegistration

class TeamApiTests(APITestCase):
    teams_url = reverse('teams')
    users_url = reverse('users')
    invitations_url = reverse('team_invitations')

    def setUp(self):
        self.captain = User.objects.create_user(username='captain', email='captain@example.com', password='StrongPass123!')
        self.member = User.objects.create_user(username='member', email='member@example.com', password='StrongPass123!')
        self.other_user = User.objects.create_user(username='other', email='other@example.com', password='StrongPass123!')
        self.admin_user = User.objects.create_user(username='admin', email='admin@example.com', password='StrongPass123!', role='admin', is_staff=True, is_superuser=True)

    def _create_team(self, payload):
        self.client.force_authenticate(user=self.captain)
        response = self.client.post(self.teams_url, payload, format='json')
        return response.data

    def _register_team_in_active_tournament(self, *, team_id, tournament_status, min_team_members=None):
        now = timezone.now()
        tournament = Tournament.objects.create(name=f'T {team_id}', start_date=now, end_date=now + timedelta(days=7), status=tournament_status, min_team_members=min_team_members, created_by=self.admin_user)
        TournamentTeamRegistration.objects.create(tournament=tournament, team_id=team_id, created_by=self.captain)
        return tournament

    def test_create_team_creates_invitations(self):
        self.client.force_authenticate(user=self.captain)
        response = self.client.post(self.teams_url, {'name': 'Alpha', 'email': 'a@e.com', 'is_public': True, 'member_ids': [self.member.id]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TeamInvitation.objects.count(), 1)

    def test_create_team_rejects_duplicate_name(self):
        self._create_team({'name': 'Dup', 'email': 'd1@e.com'})
        self.client.force_authenticate(user=self.captain)
        response = self.client.post(self.teams_url, {'name': 'Dup', 'email': 'd2@e.com'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invited_user_can_accept_invitation(self):
        team = self._create_team({'name': 'Beta', 'email': 'b@e.com', 'member_ids': [self.member.id]})
        inv = TeamInvitation.objects.get(user=self.member)
        self.client.force_authenticate(user=self.member)
        response = self.client.post(reverse('team_invitation_accept', kwargs={'invitation_id': inv.id}), {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(TeamMember.objects.filter(team_id=team['id'], user=self.member).exists())

    def test_invited_user_can_decline_invitation(self):
        team = self._create_team({'name': 'Decline', 'email': 'dec@e.com', 'member_ids': [self.member.id]})
        inv = TeamInvitation.objects.get(user=self.member)
        self.client.force_authenticate(user=self.member)
        response = self.client.post(reverse('team_invitation_decline', kwargs={'invitation_id': inv.id}), {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        inv.refresh_from_db()
        self.assertEqual(inv.status, TeamInvitation.STATUS_DECLINED)

    def test_captain_cannot_leave_team(self):
        team = self._create_team({'name': 'C', 'email': 'c@e.com'})
        self.client.force_authenticate(user=self.captain)
        response = self.client.post(reverse('team_leave', kwargs={'pk': team['id']}), {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_member_can_leave_team(self):
        team = self._create_team({'name': 'Leave', 'email': 'l@e.com', 'member_ids': [self.member.id]})
        inv = TeamInvitation.objects.get(user=self.member)
        self.client.force_authenticate(user=self.member)
        self.client.post(reverse('team_invitation_accept', kwargs={'invitation_id': inv.id}), {}, format='json')
        response = self.client.post(reverse('team_leave', kwargs={'pk': team['id']}), {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(TeamMember.objects.filter(team_id=team['id'], user=self.member).exists())

    def test_admin_visibility(self):
        team = self._create_team({'name': 'P', 'email': 'p@e.com', 'is_public': False})
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.teams_url)
        self.assertIn(team['id'], [t['id'] for t in response.data])

    def test_public_team_join_request(self):
        team = self._create_team({'name': 'Public', 'email': 'pub@e.com', 'is_public': True})
        self.client.force_authenticate(user=self.member)
        response = self.client.post(reverse('team_join_request_create', kwargs={'pk': team['id']}), {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(TeamJoinRequest.objects.filter(team_id=team['id'], user=self.member).exists())

    def test_captain_can_accept_join_request(self):
        team = self._create_team({'name': 'AcceptJoin', 'email': 'aj@e.com', 'is_public': True})
        self.client.force_authenticate(user=self.member)
        self.client.post(reverse('team_join_request_create', kwargs={'pk': team['id']}), {}, format='json')
        req = TeamJoinRequest.objects.get(team_id=team['id'], user=self.member)
        self.client.force_authenticate(user=self.captain)
        response = self.client.post(reverse('team_join_request_accept', kwargs={'pk': team['id'], 'request_id': req.id}), {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(TeamMember.objects.filter(team_id=team['id'], user=self.member).exists())

    def test_invite_blocked_in_active_tournament(self):
        team = self._create_team({'name': 'B', 'email': 'b@e.com'})
        self._register_team_in_active_tournament(team_id=team['id'], tournament_status=Tournament.STATUS_RUNNING)
        self.client.force_authenticate(user=self.captain)
        response = self.client.post(reverse('team_members', kwargs={'pk': team['id']}), {'user_id': self.member.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_member_removal_blocked_at_min_members(self):
        team = self._create_team({'name': 'Min', 'email': 'm@e.com', 'member_ids': [self.member.id]})
        inv = TeamInvitation.objects.get(user=self.member)
        self.client.force_authenticate(user=self.member)
        self.client.post(reverse('team_invitation_accept', kwargs={'invitation_id': inv.id}), {}, format='json')
        self._register_team_in_active_tournament(team_id=team['id'], tournament_status=Tournament.STATUS_RUNNING, min_team_members=2)
        self.client.force_authenticate(user=self.captain)
        response = self.client.delete(reverse('team_member_detail', kwargs={'pk': team['id'], 'user_id': self.member.id}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_users_returns_current_users(self):
        self.client.force_authenticate(user=self.captain)
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 3)

    def test_deleting_captain_cascades_to_team(self):
        team_data = self._create_team({'name': 'Cascade', 'email': 'cas@e.com'})
        self.captain.delete()
        self.assertFalse(Team.objects.filter(id=team_data['id']).exists())
