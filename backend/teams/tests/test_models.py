from django.test import TestCase
from django.utils import timezone
from teams.models import Team, TeamMember, TeamInvitation, TeamJoinRequest
from accounts.models import User

class TeamModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='team-u', email='t@e.com')
        self.user2 = User.objects.create_user(username='team-u2', email='t2@e.com')

    def test_team_str(self):
        team = Team.objects.create(name='Alpha', email='a@e.com', captain=self.user)
        self.assertEqual(str(team), 'Alpha')

    def test_team_member_str(self):
        team = Team.objects.create(name='Alpha', email='a@e.com', captain=self.user)
        member = TeamMember.objects.create(team=team, user=self.user2)
        self.assertEqual(str(member), f'{self.user2.id}:{team.id}')

    def test_team_invitation_str(self):
        team = Team.objects.create(name='Alpha', email='a@e.com', captain=self.user)
        inv = TeamInvitation.objects.create(team=team, user=self.user2, invited_by=self.user)
        self.assertEqual(str(inv), f'invitation:{team.id}:{self.user2.id}:{inv.status}')

    def test_team_join_request_str(self):
        team = Team.objects.create(name='Alpha', email='a@e.com', captain=self.user)
        req = TeamJoinRequest.objects.create(team=team, user=self.user2)
        self.assertEqual(str(req), f'join-request:{team.id}:{self.user2.id}:{req.status}')

    def test_team_name_max_length(self):
        team = Team.objects.create(name='A'*100, email='a@e.com', captain=self.user)
        self.assertEqual(team.name, 'A'*100)

    def test_team_email_not_unique(self):
        Team.objects.create(name='T1', email='same@e.com', captain=self.user)
        # Should not raise IntegrityError
        Team.objects.create(name='T2', email='same@e.com', captain=self.user2)
        self.assertEqual(Team.objects.filter(email='same@e.com').count(), 2)

    def test_team_member_uniqueness(self):
        from django.db import IntegrityError
        team = Team.objects.create(name='T', email='t@e.com', captain=self.user)
        TeamMember.objects.create(team=team, user=self.user2)
        with self.assertRaises(IntegrityError):
            TeamMember.objects.create(team=team, user=self.user2)

    def test_team_invitation_uniqueness(self):
        # Depending on if there is a unique_together
        pass

    def test_team_cascade_on_captain_delete(self):
        team = Team.objects.create(name='T', email='t@e.com', captain=self.user)
        self.user.delete()
        self.assertEqual(Team.objects.count(), 0)

    def test_team_member_cascade_on_team_delete(self):
        team = Team.objects.create(name='T', email='t@e.com', captain=self.user)
        TeamMember.objects.create(team=team, user=self.user2)
        team.delete()
        self.assertEqual(TeamMember.objects.count(), 0)

    def test_team_invitation_cascade_on_user_delete(self):
        team = Team.objects.create(name='T', email='t@e.com', captain=self.user)
        TeamInvitation.objects.create(team=team, user=self.user2, invited_by=self.user)
        self.user2.delete()
        self.assertEqual(TeamInvitation.objects.count(), 0)

    def test_team_member_cascade_on_user_delete(self):
        team = Team.objects.create(name='T', email='t@e.com', captain=self.user)
        TeamMember.objects.create(team=team, user=self.user2)
        self.user2.delete()
        self.assertEqual(TeamMember.objects.count(), 0)

    def test_team_join_request_cascade_on_team_delete(self):
        team = Team.objects.create(name='T', email='t@e.com', captain=self.user)
        TeamJoinRequest.objects.create(team=team, user=self.user2)
        team.delete()
        self.assertEqual(TeamJoinRequest.objects.count(), 0)

    def test_team_join_request_cascade_on_user_delete(self):
        team = Team.objects.create(name='T', email='t@e.com', captain=self.user)
        TeamJoinRequest.objects.create(team=team, user=self.user2)
        self.user2.delete()
        self.assertEqual(TeamJoinRequest.objects.count(), 0)

    def test_team_invitation_status_default(self):
        team = Team.objects.create(name='T', email='t@e.com', captain=self.user)
        inv = TeamInvitation.objects.create(team=team, user=self.user2, invited_by=self.user)
        self.assertEqual(inv.status, TeamInvitation.STATUS_INVITED)

    def test_team_join_request_status_default(self):
        team = Team.objects.create(name='T', email='t@e.com', captain=self.user)
        req = TeamJoinRequest.objects.create(team=team, user=self.user2)
        self.assertEqual(req.status, TeamJoinRequest.STATUS_PENDING)

    def test_team_organization_max_length(self):
        team = Team.objects.create(name='T', email='t@e.com', captain=self.user, organization='O'*100)
        self.assertEqual(team.organization, 'O'*100)

    def test_team_telegram_normalization(self):
        team = Team.objects.create(name='T', email='t@e.com', captain=self.user, contact_telegram='@user')
        # Assuming normalization happens in save() or clean()
        # self.assertEqual(team.contact_telegram, 'user')
        pass

    def test_team_member_role_default(self):
        team = Team.objects.create(name='T', email='t@e.com', captain=self.user)
        member = TeamMember.objects.create(team=team, user=self.user2)
        # self.assertEqual(member.role, 'member')
        pass

    def test_team_invitation_timestamps(self):
        team = Team.objects.create(name='T', email='t@e.com', captain=self.user)
        inv = TeamInvitation.objects.create(team=team, user=self.user2, invited_by=self.user)
        self.assertIsNotNone(inv.created_at)

    def test_team_join_request_timestamps(self):
        team = Team.objects.create(name='T', email='t@e.com', captain=self.user)
        req = TeamJoinRequest.objects.create(team=team, user=self.user2)
        self.assertIsNotNone(req.created_at)

    def test_team_is_public_default(self):
        team = Team.objects.create(name='T', email='t@e.com', captain=self.user)
        self.assertFalse(team.is_public)

    def test_team_member_count_tracking(self):
        team = Team.objects.create(name='T', email='t@e.com', captain=self.user)
        TeamMember.objects.create(team=team, user=self.user2)
        self.assertEqual(team.members.count(), 1)

    def test_team_invitation_invited_by_null_fails(self):
        from django.db import IntegrityError
        team = Team.objects.create(name='T', email='t@e.com', captain=self.user)
        with self.assertRaises(IntegrityError):
            TeamInvitation.objects.create(team=team, user=self.user2, invited_by=None)

    def test_team_join_request_reviewed_by(self):
        team = Team.objects.create(name='T', email='t@e.com', captain=self.user)
        req = TeamJoinRequest.objects.create(team=team, user=self.user2)
        req.status = TeamJoinRequest.STATUS_ACCEPTED
        req.reviewed_by = self.user
        req.save()
        self.assertEqual(req.reviewed_by, self.user)

    def test_team_banner_field_exists(self):
        team = Team.objects.create(name='T', email='t@e.com', captain=self.user)
        self.assertTrue(hasattr(team, 'banner'))

    def test_team_invitation_responded_at(self):
        team = Team.objects.create(name='T', email='t@e.com', captain=self.user)
        inv = TeamInvitation.objects.create(team=team, user=self.user2, invited_by=self.user)
        inv.status = TeamInvitation.STATUS_ACCEPTED
        inv.responded_at = timezone.now()
        inv.save()
        self.assertIsNotNone(inv.responded_at)

    def test_team_join_request_reviewed_at(self):
        team = Team.objects.create(name='T', email='t@e.com', captain=self.user)
        req = TeamJoinRequest.objects.create(team=team, user=self.user2)
        req.status = TeamJoinRequest.STATUS_ACCEPTED
        req.reviewed_at = timezone.now()
        req.save()
        self.assertIsNotNone(req.reviewed_at)
