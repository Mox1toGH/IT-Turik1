from django.test import TestCase
from accounts.models import User
from teams.models import Team
from tournaments.models import Tournament, Round, TournamentTeamRegistration
from points.models import PointsTransaction

class TournamentPointsIntegrationTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user('admin_int', 'admin_int@e.com', 'pass', role='admin')
        self.user1 = User.objects.create_user('user1_int', 'u1@e.com', 'pass')
        self.team = Team.objects.create(name='Int Team', email='int@e.com', captain=self.user1)
        
        from django.utils import timezone
        import datetime
        now = timezone.now()
        self.tournament = Tournament.objects.create(
            name='Int Tournament', 
            status=Tournament.STATUS_RUNNING, 
            start_date=now - datetime.timedelta(days=1),
            end_date=now + datetime.timedelta(days=1),
            created_by=self.admin
        )
        TournamentTeamRegistration.objects.create(
            tournament=self.tournament, 
            team=self.team, 
            is_active=True
        )

    def test_tournament_completion_awards_points(self):
        from points.services import award_tournament_points
        from points.models import UserPointsBalance, PointsTransaction

        self.tournament.status = Tournament.STATUS_FINISHED
        self.tournament.save()

        award_tournament_points(tournament=self.tournament)

        balance = UserPointsBalance.objects.filter(user=self.user1).first()
        self.assertIsNotNone(balance)
        self.assertEqual(balance.balance, 10)

        transaction = PointsTransaction.objects.filter(user=self.user1, reason__contains='Tournament participation').first()
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.amount, 10)
