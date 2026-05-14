import re
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.core import mail
from django.utils import timezone
from accounts.models import User
from teams.models import Team, TeamMember, TeamInvitation, TeamJoinRequest
from tournaments.models import Tournament, Round, TournamentTeamRegistration, Submission
from evaluation.models import JuryAssignment
from notifications.models import Notification, UserNotificationSettings, NotificationConfig
from notifications.services import NotificationService
from notifications.channels import SystemChannel, EmailChannel, _get_action, _strip_notification_tags
from notifications.config import EVENTS

class NotificationConfigTests(TestCase):
    def test_all_events_valid(self):
        """Ensure all registered events have required fields and valid formats."""
        for key, event in EVENTS.items():
            self.assertEqual(key, event.key)
            self.assertTrue(event.channels)
            self.assertTrue(event.title_tpl)
            self.assertTrue(event.message_tpl)
            if 'email' in event.channels:
                self.assertTrue(event.email_subject_tpl)

class NotificationServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')

    @patch('notifications.services.transaction.get_connection')
    @patch('notifications.services._NOTIFICATION_EXECUTOR.submit')
    def test_notify_async_by_default(self, mock_submit, mock_get_conn):
        """NotificationService.notify should use ThreadPoolExecutor by default."""
        # Mock in_atomic_block to False so it calls _submit_job immediately
        mock_get_conn.return_value.in_atomic_block = False
        
        NotificationService.notify(recipients=[self.user], event_type='team_invitation_received', context={'team_name': 'Test Team', 'invited_by': 'admin'})
        self.assertTrue(mock_submit.called)

    @override_settings(NOTIFICATIONS_ASYNC=False)
    def test_notify_sync_when_disabled(self):
        """NotificationService.notify should run synchronously if NOTIFICATIONS_ASYNC is False."""
        with patch.object(NotificationService, '_dispatch') as mock_dispatch:
            NotificationService.notify(recipients=[self.user], event_type='team_invitation_received', context={'team_name': 'Test Team', 'invited_by': 'admin'})
            self.assertTrue(mock_dispatch.called)

class ChannelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')

    def test_system_channel_creates_notification(self):
        channel = SystemChannel()
        channel.send(recipient=self.user, title='Test Title', message='Test Message', event_type='news_published')
        
        self.assertEqual(Notification.objects.count(), 1)
        notif = Notification.objects.first()
        self.assertEqual(notif.recipient, self.user)
        self.assertEqual(notif.title, 'Test Title')
        self.assertEqual(notif.message, 'Test Message')

    def test_email_channel_sends_mail(self):
        channel = EmailChannel()
        channel.send(recipient=self.user, title='Test Title', message='Test Message', event_type='news_published')
        
        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]
        self.assertEqual(sent_email.to, [self.user.email])
        self.assertIn('Test Title', sent_email.subject)
        self.assertIn('Test Message', sent_email.body)

    def test_strip_notification_tags(self):
        text = "User [user:1:John] joined [team:2:Alpha:public] in [tournament:3:Cup] for [news:4:Update]"
        stripped = _strip_notification_tags(text)
        self.assertEqual(stripped, "User John joined Alpha in Cup for Update")

    def test_get_action_routing(self):
        # Teams general
        self.assertEqual(_get_action('team_invitation_received', 'msg')[1], '/teams')
        # News
        self.assertEqual(_get_action('news_published', 'msg')[1], '/news')
        # Tournament specific
        self.assertEqual(_get_action('tournament_team_registered', '[tournament:42:X]')[1], '/tournaments/42')
        # Team specific
        self.assertEqual(_get_action('team_invitation_accepted', '[team:7:Y]')[1], '/teams/7')

@override_settings(NOTIFICATIONS_ASYNC=False)
class NotificationIntegrationTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin', email='admin@example.com', password='password123', role='admin', is_staff=True, is_superuser=True)
        self.captain = User.objects.create_user(username='captain', email='cap@example.com', password='password123')
        self.member = User.objects.create_user(username='member', email='mem@example.com', password='password123')
        self.jury = User.objects.create_user(username='jury', email='jury@example.com', password='password123', role='jury')
        
        self.team = Team.objects.create(name='Test Team', captain=self.captain)
        TeamMember.objects.create(team=self.team, user=self.captain)
        TeamMember.objects.create(team=self.team, user=self.member)
        
        self.tournament = Tournament.objects.create(
            name='Test Tournament', 
            created_by=self.admin,
            status=Tournament.STATUS_REGISTRATION,
            start_date=timezone.now() + timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=10)
        )
        self.round = Round.objects.create(
            tournament=self.tournament,
            name='Round 1',
            status=Round.STATUS_DRAFT,
            start_date=timezone.now() + timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=2)
        )

    def test_team_registration_notification(self):
        from tournaments.services import register_team_for_tournament
        Notification.objects.all().delete()
        
        register_team_for_tournament(tournament=self.tournament, team=self.team, actor=self.captain)
        
        # Notifications should be sent to captain and member
        notifs = Notification.objects.filter(event_type='tournament_team_registered')
        self.assertEqual(notifs.count(), 2)
        recipients = set(notifs.values_list('recipient_id', flat=True))
        self.assertIn(self.captain.id, recipients)
        self.assertIn(self.member.id, recipients)

    def test_team_leave_notification(self):
        from tournaments.services import register_team_for_tournament, leave_team_from_tournament
        register_team_for_tournament(tournament=self.tournament, team=self.team, actor=self.captain)
        Notification.objects.all().delete()
        
        leave_team_from_tournament(tournament=self.tournament, team=self.team, actor=self.captain)
        
        notifs = Notification.objects.filter(event_type='tournament_team_left')
        self.assertEqual(notifs.count(), 2)

    def test_round_started_notification(self):
        from tournaments.services import register_team_for_tournament, start_round
        register_team_for_tournament(tournament=self.tournament, team=self.team, actor=self.captain)
        Notification.objects.all().delete()
        
        # Round needs start_date in past to start via service
        self.round.start_date = timezone.now() - timezone.timedelta(minutes=5)
        self.round.save()
        
        start_round(self.round)
        
        notifs = Notification.objects.filter(event_type='tournament_round_started')
        self.assertEqual(notifs.count(), 2)

    def test_round_submission_closed_notification(self):
        from tournaments.services import register_team_for_tournament, start_round, close_submissions_on_round
        register_team_for_tournament(tournament=self.tournament, team=self.team, actor=self.captain)
        self.round.start_date = timezone.now() - timezone.timedelta(minutes=5)
        self.round.save()
        start_round(self.round)
        Notification.objects.all().delete()
        
        close_submissions_on_round(self.round)
        
        notifs = Notification.objects.filter(event_type='tournament_round_submission_closed')
        self.assertEqual(notifs.count(), 2)

    def test_jury_assignment_notification(self):
        from tournaments.services import register_team_for_tournament, start_round, close_submissions_on_round
        from evaluation.services import replace_round_jury_assignments
        
        register_team_for_tournament(tournament=self.tournament, team=self.team, actor=self.captain)
        self.round.start_date = timezone.now() - timezone.timedelta(minutes=5)
        self.round.save()
        start_round(self.round)
        
        # Create submission
        sub = Submission.objects.create(team=self.team, round=self.round, created_by=self.captain, github_url='http://h.com')
        
        # Must close submissions before assignment
        self.round.status = Round.STATUS_SUBMISSION_CLOSED
        self.round.save()
        
        Notification.objects.all().delete()
        
        replace_round_jury_assignments(self.round, [{'submission': sub, 'jury': [self.jury.id]}])
        
        notifs = Notification.objects.filter(event_type='jury_assignment_created', recipient=self.jury)
        self.assertEqual(notifs.count(), 1)
        self.assertIn(self.tournament.name, notifs.first().message)

    def test_round_evaluated_and_eliminated_notifications(self):
        from tournaments.services import register_team_for_tournament, start_round, close_submissions_on_round, mark_round_evaluated
        from evaluation.services import replace_round_jury_assignments
        from evaluation.models import SubmissionEvaluation
        
        # Team 1 (Captain + Member) - will PASS
        register_team_for_tournament(tournament=self.tournament, team=self.team, actor=self.captain)
        
        # Team 2 (Other Captain) - will be ELIMINATED
        other_cap = User.objects.create_user(username='othercap', email='othercap@example.com', password='password123')
        other_team = Team.objects.create(name='Other Team', captain=other_cap)
        TeamMember.objects.create(team=other_team, user=other_cap)
        register_team_for_tournament(tournament=self.tournament, team=other_team, actor=other_cap)
        
        self.round.start_date = timezone.now() - timezone.timedelta(minutes=5)
        self.round.passing_count = 1 # Only 1 team passes
        self.round.save()
        
        sub1 = Submission.objects.create(team=self.team, round=self.round, created_by=self.captain, github_url='http://h1.com')
        sub2 = Submission.objects.create(team=other_team, round=self.round, created_by=other_cap, github_url='http://h2.com')
        
        # Close submissions
        self.round.status = Round.STATUS_SUBMISSION_CLOSED
        self.round.save()
        
        replace_round_jury_assignments(self.round, [
            {'submission': sub1, 'jury': [self.jury.id]},
            {'submission': sub2, 'jury': [self.jury.id]}
        ])
        
        # Evaluate: Team 1 gets 10, Team 2 gets 5
        as1 = JuryAssignment.objects.get(submission=sub1, jury=self.jury)
        SubmissionEvaluation.objects.create(assignment=as1, scores=[{'score': 10}], comment='Great')
        
        as2 = JuryAssignment.objects.get(submission=sub2, jury=self.jury)
        SubmissionEvaluation.objects.create(assignment=as2, scores=[{'score': 5}], comment='Bad')
        
        Notification.objects.all().delete()
        
        mark_round_evaluated(self.round)
        
        # Should have 'evaluated' notification for the passing team members (captain + member)
        eval_notifs = Notification.objects.filter(event_type='tournament_round_evaluated')
        self.assertEqual(eval_notifs.count(), 2)
        
        # Should have 'eliminated' notification for the eliminated team (other_cap)
        elim_notifs = Notification.objects.filter(event_type='tournament_round_eliminated')
        self.assertEqual(elim_notifs.count(), 1)
        self.assertEqual(elim_notifs.first().recipient, other_cap)

    def test_tournament_finished_notification(self):
        from tournaments.services import register_team_for_tournament, start_round, close_submissions_on_round, mark_round_evaluated
        from evaluation.services import replace_round_jury_assignments
        from evaluation.models import SubmissionEvaluation
        
        register_team_for_tournament(tournament=self.tournament, team=self.team, actor=self.captain)
        self.round.start_date = timezone.now() - timezone.timedelta(minutes=5)
        self.round.save()
        start_round(self.round)
        sub = Submission.objects.create(team=self.team, round=self.round, created_by=self.captain, github_url='http://h.com')
        
        # Close submissions
        self.round.status = Round.STATUS_SUBMISSION_CLOSED
        self.round.save()
        
        replace_round_jury_assignments(self.round, [{'submission': sub, 'jury': [self.jury.id]}])
        assignment = JuryAssignment.objects.get(submission=sub, jury=self.jury)
        SubmissionEvaluation.objects.create(
            assignment=assignment, 
            scores=[{'criterion': 'Test', 'score': 5}],
            comment='Good'
        )
        
        Notification.objects.all().delete()
        
        mark_round_evaluated(self.round)
        
        # Tournament has only 1 round, so it should finish
        self.assertEqual(self.tournament.rounds.count(), 1)
        self.tournament.refresh_from_db()
        self.assertEqual(self.tournament.status, Tournament.STATUS_FINISHED)
        
        notifs = Notification.objects.filter(event_type='tournament_finished')
        self.assertTrue(notifs.exists())

    def test_team_disqualified_notification(self):
        from tournaments.services import register_team_for_tournament
        register_team_for_tournament(tournament=self.tournament, team=self.team, actor=self.captain)
        
        reg = TournamentTeamRegistration.objects.get(tournament=self.tournament, team=self.team)
        
        Notification.objects.all().delete()
        
        # Use view-like logic or direct signal send because views are harder to test in isolation for signals
        from tournaments.signals import tournament_team_disqualified
        tournament_team_disqualified.send(sender=None, tournament=self.tournament, team=self.team, reason='Cheating')
        
        notifs = Notification.objects.filter(event_type='tournament_team_disqualified')
        self.assertEqual(notifs.count(), 2)
        self.assertIn('Cheating', notifs.first().message)
