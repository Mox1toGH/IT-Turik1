from django.test import TestCase
from accounts.models import User
from teams.models import Team, TeamMember, TeamJoinRequest

class TeamEdgeCasesTests(TestCase):
    def setUp(self):
        self.captain = User.objects.create_user('captain_edge', 'cap@e.com', 'pass')
        self.user1 = User.objects.create_user('user1_edge', 'u1@e.com', 'pass')
        self.team = Team.objects.create(name='Edge Team', email='edge@e.com', captain=self.captain)

    def test_user_cannot_join_own_team_again(self):
        # Already captain, technically a member (implicit or explicit depending on implementation)
        from django.db import IntegrityError
        # Assuming captain is added to members explicitly in some services
        # We test if adding them again raises IntegrityError
        TeamMember.objects.create(team=self.team, user=self.captain)
        with self.assertRaises(IntegrityError):
            TeamMember.objects.create(team=self.team, user=self.captain)

    def test_duplicate_join_request_fails(self):
        from django.db import IntegrityError
        TeamJoinRequest.objects.create(team=self.team, user=self.user1)
        with self.assertRaises(IntegrityError):
            TeamJoinRequest.objects.create(team=self.team, user=self.user1)
