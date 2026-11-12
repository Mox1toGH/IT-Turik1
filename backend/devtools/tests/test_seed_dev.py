"""Tests for the ``seed_dev`` management command."""

from io import StringIO
import weakref

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, TransactionTestCase, override_settings

from accounts.models import User
from devtools.management.commands.seed_dev import Command
from devtools.seeders.base import SEED_EMAIL_DOMAIN, SEED_PASSWORD, SIZE_PROFILES
from evaluation.models import JuryAssignment, LeaderboardEntry
from news.models import NewsArticle
from teams.models import Team, TeamInvitation, TeamJoinRequest, TeamMember
from tournaments.models import Round, Submission, Tournament, TournamentTeamRegistration


class SeedDevSafetyTests(TestCase):
    def test_local_sqlite_is_allowed_when_debug_false(self):
        with override_settings(DEBUG=False):
            Command()._check_safety()

    def test_refused_for_non_sqlite_database_even_when_debug_true(self):
        database = {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'itturik',
            'HOST': 'production.example.com',
        }
        with override_settings(DEBUG=True, DATABASES={'default': database}):
            with self.assertRaisesMessage(CommandError, 'only local SQLite'):
                call_command('seed_dev', '--size', 'small')

    def test_refused_for_production_named_sqlite_database_even_when_debug_true(self):
        database = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'production.sqlite3',
        }
        with override_settings(DEBUG=True, DATABASES={'default': database}):
            with self.assertRaisesMessage(CommandError, 'looks like production'):
                call_command('seed_dev', '--size', 'small')

    def test_unknown_area_is_rejected(self):
        with self.assertRaises(CommandError):
            call_command('seed_dev', '--only', 'nonsense', '--size', 'small')


@override_settings(DEBUG=True)
class SeedDevCommandTests(TransactionTestCase):
    """Run one small seed and verify its data, idempotency, and reset behavior."""

    available_apps = None

    def _run(self, *args):
        out = StringIO()
        call_command('seed_dev', *args, stdout=out, stderr=out)
        return out.getvalue()

    def _counts(self):
        return {
            'users': User.objects.filter(email__endswith=SEED_EMAIL_DOMAIN).count(),
            'teams': Team.objects.count(),
            'tournaments': Tournament.objects.count(),
            'rounds': Round.objects.count(),
            'submissions': Submission.objects.count(),
            'news': NewsArticle.objects.count(),
        }

    def _assert_scenario_dataset(self):
        scenario_teams = Team.objects.filter(name__contains=' — ')
        for name in (
            'Team — Captain Only (No Members Yet)',
            'Team — Pending Invitation',
            'Team — Accepted Invitation',
            'Team — Declined Invitation',
            'Team — Pending Join Requests',
            'Team — Accepted Join Request',
            'Team — Declined Join Request',
            'Team — Private (Hidden From List)',
        ):
            self.assertTrue(scenario_teams.filter(name=name).exists(), name)

        scenario_tournaments = Tournament.objects.filter(name__contains=' — ')
        self.assertEqual(scenario_tournaments.count(), 7)
        for name in (
            'Tournament — No Registrations Yet',
            'Tournament — Mixed Registration States',
            'Tournament — Full At Max Teams',
            'Tournament — Running With Disqualified Team',
            'Tournament — Running With Cancelled Registration',
            'Tournament — Finished With Final Standings',
            'Tournament — Draft Without Rounds',
        ):
            self.assertTrue(scenario_tournaments.filter(name=name).exists(), name)

        self.assertEqual(
            set(scenario_tournaments.values_list('status', flat=True)),
            {
                Tournament.STATUS_DRAFT,
                Tournament.STATUS_REGISTRATION,
                Tournament.STATUS_RUNNING,
                Tournament.STATUS_FINISHED,
            },
        )
        self.assertEqual(
            set(Round.objects.filter(name__contains=' — ').values_list('status', flat=True)),
            {
                Round.STATUS_DRAFT,
                Round.STATUS_ACTIVE,
                Round.STATUS_SUBMISSION_CLOSED,
                Round.STATUS_EVALUATED,
            },
        )

        pending = TeamInvitation.objects.get(
            team__name='Team — Pending Invitation',
            status=TeamInvitation.STATUS_INVITED,
        )
        self.assertIsNone(pending.responded_at)
        self.assertFalse(TeamMember.objects.filter(team=pending.team, user=pending.user).exists())

        accepted = TeamInvitation.objects.get(
            team__name='Team — Accepted Invitation',
            status=TeamInvitation.STATUS_ACCEPTED,
        )
        self.assertIsNotNone(accepted.responded_at)
        self.assertTrue(TeamMember.objects.filter(team=accepted.team, user=accepted.user).exists())

        declined = TeamInvitation.objects.get(
            team__name='Team — Declined Invitation',
            status=TeamInvitation.STATUS_DECLINED,
        )
        self.assertIsNotNone(declined.responded_at)
        self.assertFalse(TeamMember.objects.filter(team=declined.team, user=declined.user).exists())

        request = TeamJoinRequest.objects.get(
            team__name='Team — Accepted Join Request',
            status=TeamJoinRequest.STATUS_ACCEPTED,
        )
        self.assertIsNotNone(request.reviewed_by_id)
        self.assertIsNotNone(request.reviewed_at)

        disqualified = TournamentTeamRegistration.objects.get(
            tournament__name='Tournament — Running With Disqualified Team',
            is_disqualified=True,
        )
        self.assertFalse(disqualified.is_active)
        self.assertTrue(disqualified.disqualification_reason)
        for registration in TournamentTeamRegistration.objects.filter(is_active=True):
            self.assertFalse(registration.is_disqualified)

        full = Tournament.objects.get(name='Tournament — Full At Max Teams')
        self.assertEqual(
            full.team_registrations.filter(is_active=True).count(),
            full.max_teams,
        )

        active_statuses = (Tournament.STATUS_REGISTRATION, Tournament.STATUS_RUNNING)
        teams_in_active_tournaments = {}
        for registration in TournamentTeamRegistration.objects.filter(
            tournament__status__in=active_statuses,
            is_active=True,
        ).select_related('team'):
            self.assertNotIn(registration.team_id, teams_in_active_tournaments)
            teams_in_active_tournaments[registration.team_id] = registration.tournament_id

        for submission in Submission.objects.filter(team__name__contains=' — '):
            self.assertEqual(submission.created_by_id, submission.team.captain_id)
            self.assertTrue(submission.github_url)
            self.assertTrue(submission.demo_video_url or submission.demo_video_file)

        finished = Tournament.objects.get(name='Tournament — Finished With Final Standings')
        for round_obj in finished.rounds.all():
            self.assertEqual(round_obj.status, Round.STATUS_EVALUATED)
        self.assertTrue(
            LeaderboardEntry.objects.filter(tournament=finished, round__isnull=True).exists()
        )

        elimination_round = finished.rounds.get(name__icontains='Rank Elimination')
        eliminated = finished.team_registrations.filter(
            is_active=False,
            disqualification_reason__icontains='Eliminated by rank',
        )
        self.assertTrue(eliminated.exists())
        self.assertEqual(
            elimination_round.passing_count,
            finished.team_registrations.filter(is_active=True).count(),
        )

        for assignment in JuryAssignment.objects.all():
            self.assertEqual(assignment.jury.role, 'jury')
            evaluation = getattr(assignment, 'evaluation', None)
            if evaluation is None:
                continue
            criterion_ids = {item['id'] for item in assignment.submission.round.criteria}
            score_ids = {item['criterion_id'] for item in evaluation.scores}
            self.assertEqual(score_ids, criterion_ids)
            self.assertEqual(
                evaluation.total_score,
                sum(item['score'] for item in evaluation.scores),
            )

        for tournament in Tournament.objects.all():
            active_rounds = tournament.rounds.filter(status=Round.STATUS_ACTIVE)
            self.assertLessEqual(active_rounds.count(), 1)

        for round_obj in Round.objects.filter(name__contains=' — '):
            self.assertGreaterEqual(round_obj.start_date, round_obj.tournament.start_date)
            self.assertLessEqual(round_obj.end_date, round_obj.tournament.end_date)
            self.assertLess(round_obj.start_date, round_obj.end_date)

        allowed_nodes = {
            'doc', 'paragraph', 'heading', 'blockquote', 'codeBlock', 'bulletList',
            'orderedList', 'listItem', 'horizontalRule', 'hardBreak', 'text', 'link',
        }
        allowed_marks = {
            'bold', 'italic', 'underline', 'strike', 'code', 'highlight', 'link',
        }
        banned_nodes = {
            'image', 'table', 'tableRow', 'tableCell', 'tableHeader',
            'taskList', 'taskItem', 'mention', 'emoji',
        }

        def check_document(node, label):
            self.assertIn(node['type'], allowed_nodes, f'{label}: {node["type"]}')
            self.assertNotIn(node['type'], banned_nodes, f'{label}: {node["type"]}')
            if node['type'] == 'text':
                self.assertIsInstance(node['text'], str)
            if node['type'] == 'heading':
                self.assertIn(node['attrs']['level'], range(1, 7))
            for mark in node.get('marks') or []:
                self.assertIn(mark['type'], allowed_marks, f'{label}: {mark}')
            for child in node.get('content') or []:
                check_document(child, label)

        documents = 0
        for round_obj in Round.objects.filter(name__contains=' — '):
            for field in ('description', 'tech_requirements', 'must_have_requirements'):
                document = getattr(round_obj, field)
                self.assertIsInstance(document, dict)
                self.assertEqual(document['type'], 'doc')
                self.assertTrue(document.get('content'))
                check_document(document, f'{round_obj.name}.{field}')
                documents += 1
        for article in NewsArticle.objects.filter(title__contains=' — '):
            self.assertEqual(article.content['type'], 'doc')
            check_document(article.content, article.title)
            documents += 1
        self.assertGreater(documents, 0)

        from django.db.models.signals import post_save
        from tournaments.models import Event
        from tournaments.signals import (
            sync_event_to_google_calendar,
            sync_round_to_google_calendar,
        )

        def is_connected(receiver):
            for entry in post_save.receivers:
                for slot in entry:
                    candidate = slot() if isinstance(slot, weakref.ReferenceType) else slot
                    if candidate is receiver:
                        return True
            return False

        self.assertTrue(is_connected(sync_event_to_google_calendar))
        self.assertTrue(is_connected(sync_round_to_google_calendar))

    def test_seed_data_and_rerun_behaviors(self):
        seed = '--seed'
        output = self._run('--size', 'small', seed, '99', '--reset')
        self.assertIn('=== Seeded scenarios ===', output)
        self.assertIn('=== Record summary ===', output)
        self.assertIn('=== Seed accounts ===', output)
        self.assertIn(f'Bulk volume: {SIZE_PROFILES["small"].describe}', output)
        self.assertIn(SEED_PASSWORD, output)
        self.assertIn('admin@seed.local', output)
        self._assert_scenario_dataset()

        initial_counts = self._counts()
        initial_urls = sorted(Submission.objects.values_list('github_url', flat=True))

        self._run('--size', 'small', seed, '99')
        self.assertEqual(self._counts(), initial_counts)
        self.assertEqual(
            sorted(Submission.objects.values_list('github_url', flat=True)),
            initial_urls,
        )

        self._run('--size', 'small', seed, '99', '--reset')
        self.assertEqual(self._counts(), initial_counts)
        self.assertEqual(
            sorted(Submission.objects.values_list('github_url', flat=True)),
            initial_urls,
        )
        self.assertEqual(Tournament.objects.filter(name__contains=' — ').count(), 7)
