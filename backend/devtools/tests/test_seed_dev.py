"""Tests for the ``seed_dev`` management command."""

from io import StringIO
import weakref

from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection
from django.test import TestCase, TransactionTestCase, override_settings

from accounts.models import User
from devtools.seeders.base import SEED_EMAIL_DOMAIN, SEED_PASSWORD, SIZES, SIZE_PROFILES
from evaluation.models import JuryAssignment, LeaderboardEntry, SubmissionEvaluation
from news.models import NewsArticle
from teams.models import Team, TeamInvitation, TeamJoinRequest, TeamMember
from tournaments.models import Round, Submission, Tournament, TournamentTeamRegistration


class SeedDevSafetyTests(TestCase):
    def test_refused_when_debug_false(self):
        with override_settings(DEBUG=False):
            with self.assertRaises(CommandError):
                call_command('seed_dev', '--size', 'small')


@override_settings(DEBUG=True)
class SeedDevCommandTests(TransactionTestCase):
    """Seeding touches a lot of rows, so this needs real commits.

    ``TransactionTestCase`` is required because the command wraps its work in
    an atomic block that also starts and finishes rounds.

    ``DEBUG=True`` is set because Django's test runner forces ``DEBUG=False``,
    which is exactly what the command's safety guard refuses. The guard itself
    is covered separately by ``SeedDevSafetyTests``.
    """

    available_apps = None

    def _run(self, *args):
        out = StringIO()
        call_command('seed_dev', *args, stdout=out, stderr=out)
        return out.getvalue()

    def test_seeds_every_size_without_errors(self):
        for size in SIZES:
            with self.subTest(size=size):
                self._run('--size', size, '--reset')
                self.assertTrue(
                    User.objects.filter(email__endswith=SEED_EMAIL_DOMAIN).exists()
                )

    def test_summary_reports_the_selected_size(self):
        for size in SIZES:
            with self.subTest(size=size):
                output = self._run('--size', size, '--reset')
                self.assertIn('=== Seeded scenarios ===', output)
                self.assertIn('=== Record summary ===', output)
                self.assertIn('=== Seed accounts ===', output)
                self.assertIn(f'Bulk volume: {SIZE_PROFILES[size].describe}', output)

    def test_accounts_table_lists_role_and_password(self):
        output = self._run('--size', 'small', '--reset')
        self.assertIn(SEED_PASSWORD, output)
        self.assertIn('admin@seed.local', output)

    def test_running_twice_does_not_duplicate(self):
        self._run('--size', 'small', '--reset')
        counts = {
            'users': User.objects.filter(email__endswith=SEED_EMAIL_DOMAIN).count(),
            'teams': Team.objects.count(),
            'tournaments': Tournament.objects.count(),
            'rounds': Round.objects.count(),
            'submissions': Submission.objects.count(),
            'news': NewsArticle.objects.count(),
        }
        self._run('--size', 'small')
        self.assertEqual(
            counts['users'], User.objects.filter(email__endswith=SEED_EMAIL_DOMAIN).count()
        )
        self.assertEqual(counts['teams'], Team.objects.count())
        self.assertEqual(counts['tournaments'], Tournament.objects.count())
        self.assertEqual(counts['rounds'], Round.objects.count())
        self.assertEqual(counts['submissions'], Submission.objects.count())
        self.assertEqual(counts['news'], NewsArticle.objects.count())

    def test_larger_size_produces_more_bulk_data(self):
        self._run('--size', 'small', '--reset')
        small_users = User.objects.filter(email__endswith=SEED_EMAIL_DOMAIN).count()
        self._run('--size', 'large', '--reset')
        large_users = User.objects.filter(email__endswith=SEED_EMAIL_DOMAIN).count()
        self.assertGreater(large_users, small_users)

    def test_all_scenarios_present_at_every_size(self):
        for size in SIZES:
            with self.subTest(size=size):
                self._run('--size', size, '--reset')
                scenario_teams = Team.objects.filter(name__contains=' — ')
                self.assertGreaterEqual(scenario_teams.count(), 9)
                for expected in (
                    'Team — Captain Only (No Members Yet)',
                    'Team — Pending Invitation',
                    'Team — Accepted Invitation',
                    'Team — Declined Invitation',
                    'Team — Pending Join Requests',
                    'Team — Accepted Join Request',
                    'Team — Declined Join Request',
                    'Team — Private (Hidden From List)',
                ):
                    self.assertTrue(
                        scenario_teams.filter(name=expected).exists(),
                        f'{expected} missing at size {size}',
                    )
                for expected in (
                    'Tournament — No Registrations Yet',
                    'Tournament — Mixed Registration States',
                    'Tournament — Full At Max Teams',
                    'Tournament — Running With Disqualified Team',
                    'Tournament — Running With Cancelled Registration',
                    'Tournament — Finished With Final Standings',
                    'Tournament — Draft Without Rounds',
                ):
                    self.assertTrue(
                        Tournament.objects.filter(name=expected).exists(),
                        f'{expected} missing at size {size}',
                    )

    def test_tournament_statuses_cover_every_value(self):
        self._run('--size', 'small', '--reset')
        seeded = Tournament.objects.filter(name__contains=' — ')
        self.assertEqual(
            set(seeded.values_list('status', flat=True)),
            {
                Tournament.STATUS_DRAFT,
                Tournament.STATUS_REGISTRATION,
                Tournament.STATUS_RUNNING,
                Tournament.STATUS_FINISHED,
            },
        )

    def test_round_statuses_cover_every_value(self):
        self._run('--size', 'small', '--reset')
        seeded = Round.objects.filter(name__contains=' — ')
        self.assertEqual(
            set(seeded.values_list('status', flat=True)),
            {
                Round.STATUS_DRAFT,
                Round.STATUS_ACTIVE,
                Round.STATUS_SUBMISSION_CLOSED,
                Round.STATUS_EVALUATED,
            },
        )

    def test_team_membership_workflow_states(self):
        self._run('--size', 'small', '--reset')

        pending = TeamInvitation.objects.get(
            team__name='Team — Pending Invitation', status=TeamInvitation.STATUS_INVITED
        )
        self.assertIsNone(pending.responded_at)
        self.assertFalse(
            TeamMember.objects.filter(team=pending.team, user=pending.user).exists()
        )

        accepted = TeamInvitation.objects.get(
            team__name='Team — Accepted Invitation', status=TeamInvitation.STATUS_ACCEPTED
        )
        self.assertIsNotNone(accepted.responded_at)
        self.assertTrue(
            TeamMember.objects.filter(team=accepted.team, user=accepted.user).exists()
        )

        declined = TeamInvitation.objects.get(
            team__name='Team — Declined Invitation', status=TeamInvitation.STATUS_DECLINED
        )
        self.assertIsNotNone(declined.responded_at)
        self.assertFalse(
            TeamMember.objects.filter(team=declined.team, user=declined.user).exists()
        )

        request = TeamJoinRequest.objects.get(
            team__name='Team — Accepted Join Request', status=TeamJoinRequest.STATUS_ACCEPTED
        )
        self.assertIsNotNone(request.reviewed_by_id)
        self.assertIsNotNone(request.reviewed_at)

    def test_registration_states_are_coherent(self):
        self._run('--size', 'small', '--reset')

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
            full.team_registrations.filter(is_active=True).count(), full.max_teams
        )

    def test_participant_exclusivity_is_respected(self):
        self._run('--size', 'small', '--reset')
        active_tournaments = [
            Tournament.STATUS_REGISTRATION,
            Tournament.STATUS_RUNNING,
        ]
        seen = {}
        for registration in TournamentTeamRegistration.objects.filter(
            tournament__status__in=active_tournaments, is_active=True
        ).select_related('team'):
            self.assertNotIn(
                registration.team_id,
                seen,
                f'{registration.team.name} is active in two tournaments',
            )
            seen[registration.team_id] = registration.tournament_id

    def test_submissions_created_by_captain_with_demo(self):
        self._run('--size', 'small', '--reset')
        for submission in Submission.objects.all():
            self.assertEqual(submission.created_by_id, submission.team.captain_id)
            self.assertTrue(submission.github_url)
            self.assertTrue(submission.demo_video_url or submission.demo_video_file)

    def test_finished_tournament_has_standings_and_evaluated_rounds(self):
        self._run('--size', 'small', '--reset')
        finished = Tournament.objects.get(name='Tournament — Finished With Final Standings')
        self.assertEqual(finished.status, Tournament.STATUS_FINISHED)
        for round_obj in finished.rounds.all():
            self.assertEqual(round_obj.status, Round.STATUS_EVALUATED)
        self.assertTrue(
            LeaderboardEntry.objects.filter(
                tournament=finished, round__isnull=True
            ).exists()
        )

    def test_rank_elimination_is_applied(self):
        self._run('--size', 'small', '--reset')
        finished = Tournament.objects.get(name='Tournament — Finished With Final Standings')
        elimination_round = finished.rounds.get(
            name__icontains='Rank Elimination'
        )
        eliminated = finished.team_registrations.filter(
            is_active=False, disqualification_reason__icontains='Eliminated by rank'
        )
        self.assertTrue(eliminated.exists())
        self.assertEqual(
            elimination_round.passing_count,
            finished.team_registrations.filter(is_active=True).count(),
        )

    def test_every_evaluation_matches_its_round_criteria(self):
        self._run('--size', 'small', '--reset')
        for assignment in JuryAssignment.objects.all():
            self.assertEqual(assignment.jury.role, 'jury')
            evaluation = getattr(assignment, 'evaluation', None)
            if evaluation is None:
                continue
            criterion_ids = {c['id'] for c in assignment.submission.round.criteria}
            score_ids = {item['criterion_id'] for item in evaluation.scores}
            self.assertEqual(score_ids, criterion_ids)
            self.assertEqual(
                evaluation.total_score,
                sum(item['score'] for item in evaluation.scores),
            )

    def test_at_most_one_active_round_per_tournament(self):
        self._run('--size', 'small', '--reset')
        for tournament in Tournament.objects.all():
            active = tournament.rounds.filter(status=Round.STATUS_ACTIVE)
            self.assertLessEqual(active.count(), 1)

    def test_rounds_sit_inside_their_tournament_window(self):
        self._run('--size', 'small', '--reset')
        for round_obj in Round.objects.filter(name__contains=' — '):
            tournament = round_obj.tournament
            self.assertGreaterEqual(round_obj.start_date, tournament.start_date)
            self.assertLessEqual(round_obj.end_date, tournament.end_date)
            self.assertLess(round_obj.start_date, round_obj.end_date)

    def test_rich_text_is_valid_tiptap_json(self):
        self._run('--size', 'small', '--reset')
        allowed_nodes = {
            'doc', 'paragraph', 'heading', 'blockquote', 'codeBlock', 'bulletList',
            'orderedList', 'listItem', 'horizontalRule', 'hardBreak', 'text', 'link',
        }
        allowed_marks = {'bold', 'italic', 'underline', 'strike', 'code', 'highlight'}

        def walk(node, label):
            self.assertIn(node['type'], allowed_nodes, f'{label}: {node["type"]}')
            if node['type'] == 'text':
                self.assertIsInstance(node['text'], str)
            if node['type'] == 'heading':
                self.assertIn(node['attrs']['level'], range(1, 7))
            for mark in node.get('marks') or []:
                self.assertIn(mark['type'], allowed_marks, f'{label}: mark {mark}')
            for index, child in enumerate(node.get('content') or []):
                walk(child, f'{label}.content[{index}]')

        documents = 0
        for round_obj in Round.objects.filter(name__contains=' — '):
            for field in ('description', 'tech_requirements', 'must_have_requirements'):
                document = getattr(round_obj, field)
                self.assertIsInstance(document, dict)
                self.assertEqual(document['type'], 'doc', f'{round_obj.name}.{field}')
                self.assertTrue(document.get('content'))
                walk(document, f'{round_obj.name}.{field}')
                documents += 1

        for article in NewsArticle.objects.filter(title__contains=' — '):
            self.assertEqual(article.content['type'], 'doc')
            walk(article.content, article.title)
            documents += 1

        self.assertGreater(documents, 0)

    def test_no_unsupported_tiptap_nodes_or_marks(self):
        """Image, table, taskList and friends are not enabled anywhere."""
        self._run('--size', 'small', '--reset')
        banned = {'image', 'table', 'tableRow', 'tableCell', 'tableHeader',
                  'taskList', 'taskItem', 'mention', 'emoji'}

        def walk(node, label):
            self.assertNotIn(node['type'], banned, f'{label}: {node["type"]}')
            for child in node.get('content') or []:
                walk(child, label)

        for round_obj in Round.objects.filter(name__contains=' — '):
            for field in ('description', 'tech_requirements', 'must_have_requirements'):
                walk(getattr(round_obj, field), f'{round_obj.name}.{field}')
        for article in NewsArticle.objects.filter(title__contains=' — '):
            walk(article.content, article.title)

    def test_google_calendar_signals_are_restored(self):
        from django.db.models.signals import post_save

        from tournaments.models import Event, Round as RoundModel
        from tournaments.signals import (
            sync_event_to_google_calendar,
            sync_round_to_google_calendar,
        )

        self._run('--size', 'small', '--reset')

        def is_connected(receiver):
            # Receiver entries hold weak references and their exact layout has
            # changed between Django versions, so dereference every slot.
            for entry in post_save.receivers:
                for slot in entry:
                    candidate = slot() if isinstance(slot, weakref.ReferenceType) else slot
                    if candidate is receiver:
                        return True
            return False

        self.assertTrue(is_connected(sync_event_to_google_calendar))
        self.assertTrue(is_connected(sync_round_to_google_calendar))

    def test_reset_removes_seeded_rows(self):
        self._run('--size', 'small', '--reset')
        self.assertTrue(Tournament.objects.filter(name__contains=' — ').exists())
        self._run('--size', 'small', '--reset')
        # Recreated, not duplicated.
        self.assertEqual(
            Tournament.objects.filter(name__contains=' — ').count(), 7
        )

    def test_only_area_selection(self):
        with self.assertRaises(CommandError):
            call_command('seed_dev', '--only', 'nonsense', '--size', 'small')

    def test_deterministic_with_same_seed(self):
        self._run('--size', 'small', '--reset', '--seed', '99')
        first = sorted(
            Submission.objects.values_list('github_url', flat=True)
        )
        self._run('--size', 'small', '--reset', '--seed', '99')
        second = sorted(
            Submission.objects.values_list('github_url', flat=True)
        )
        self.assertEqual(first, second)