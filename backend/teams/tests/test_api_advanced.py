from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from accounts.models import User
from teams.models import Team, TeamMember, TeamJoinRequest, TeamInvitation

class TeamsApiAdvancedTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user('team_admin', 't_a@e.com', 'pass', role='admin', is_staff=True)
        self.user1 = User.objects.create_user('team_user1', 't_u1@e.com', 'pass')
        self.user2 = User.objects.create_user('team_user2', 't_u2@e.com', 'pass')
        self.user3 = User.objects.create_user('team_user3', 't_u3@e.com', 'pass')
        
        self.team1 = Team.objects.create(name='Team A', email='ta@e.com', captain=self.user1, is_public=True)
        self.team2 = Team.objects.create(name='Team B', email='tb@e.com', captain=self.user2, is_public=False)
        
        self.member = TeamMember.objects.create(team=self.team1, user=self.user3)

    # 20 tests
    def test_list_teams_anonymous_sees_public(self):
        url = reverse('team-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Team A')

    def test_list_teams_authenticated_sees_all(self):
        url = reverse('team-list')
        self.client.force_authenticate(self.user3)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 2)

    def test_retrieve_public_team_anonymous(self):
        url = reverse('team-detail', kwargs={'pk': self.team1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Team A')

    def test_retrieve_private_team_anonymous_forbidden(self):
        url = reverse('team-detail', kwargs={'pk': self.team2.id})
        response = self.client.get(url)
        # It might be 401 or 404 depending on how view filters queryset
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN])

    def test_retrieve_private_team_authenticated(self):
        url = reverse('team-detail', kwargs={'pk': self.team2.id})
        self.client.force_authenticate(self.user3)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_team_authenticated(self):
        url = reverse('team-list')
        self.client.force_authenticate(self.user3)
        response = self.client.post(url, {'name': 'Team C', 'email': 'tc@e.com'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Team.objects.count(), 3)

    def test_create_team_anonymous_forbidden(self):
        url = reverse('team-list')
        response = self.client.post(url, {'name': 'Team C', 'email': 'tc@e.com'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_team_captain(self):
        url = reverse('team-detail', kwargs={'pk': self.team1.id})
        self.client.force_authenticate(self.user1)
        response = self.client.patch(url, {'name': 'Team A Updated'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_team_member_forbidden(self):
        url = reverse('team-detail', kwargs={'pk': self.team1.id})
        self.client.force_authenticate(self.user3)
        response = self.client.patch(url, {'name': 'Hacked'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_team_captain(self):
        url = reverse('team-detail', kwargs={'pk': self.team1.id})
        self.client.force_authenticate(self.user1)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_team_member_forbidden(self):
        url = reverse('team-detail', kwargs={'pk': self.team1.id})
        self.client.force_authenticate(self.user3)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_join_request_authenticated(self):
        url = reverse('team-join-requests', kwargs={'pk': self.team2.id})
        self.client.force_authenticate(self.user3)
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_join_request_already_member(self):
        url = reverse('team-join-requests', kwargs={'pk': self.team1.id})
        self.client.force_authenticate(self.user3)
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_captain_can_view_join_requests(self):
        TeamJoinRequest.objects.create(team=self.team2, user=self.user3)
        url = reverse('team-join-requests', kwargs={'pk': self.team2.id})
        self.client.force_authenticate(self.user2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_member_cannot_view_join_requests(self):
        TeamJoinRequest.objects.create(team=self.team1, user=self.user2)
        url = reverse('team-join-requests', kwargs={'pk': self.team1.id})
        self.client.force_authenticate(self.user3)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_captain_can_accept_join_request(self):
        req = TeamJoinRequest.objects.create(team=self.team2, user=self.user3)
        url = reverse('team-join-request-detail', kwargs={'team_pk': self.team2.id, 'pk': req.id})
        self.client.force_authenticate(self.user2)
        response = self.client.patch(url, {'status': 'accepted'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        req.refresh_from_db()
        self.assertEqual(req.status, 'accepted')

    def test_member_cannot_accept_join_request(self):
        req = TeamJoinRequest.objects.create(team=self.team1, user=self.user2)
        url = reverse('team-join-request-detail', kwargs={'team_pk': self.team1.id, 'pk': req.id})
        self.client.force_authenticate(self.user3)
        response = self.client.patch(url, {'status': 'accepted'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_captain_can_remove_member(self):
        url = reverse('team-member-detail', kwargs={'team_pk': self.team1.id, 'pk': self.member.id})
        self.client.force_authenticate(self.user1)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_member_can_leave_team(self):
        url = reverse('team-member-detail', kwargs={'team_pk': self.team1.id, 'pk': self.member.id})
        self.client.force_authenticate(self.user3)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_member_cannot_remove_other_member(self):
        m2 = TeamMember.objects.create(team=self.team1, user=self.user2)
        url = reverse('team-member-detail', kwargs={'team_pk': self.team1.id, 'pk': m2.id})
        self.client.force_authenticate(self.user3)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
