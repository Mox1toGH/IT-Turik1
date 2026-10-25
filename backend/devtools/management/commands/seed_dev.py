"""Populate a development database with realistic, scenario-named data.

The dataset is organised around recognisable application states rather than
arbitrary records, so a developer can open the running application and inspect
each business state directly. Every generated entity is named after the
scenario it demonstrates, for example ``Team — With Pending Invitations``.

Usage::

    python manage.py seed_dev                          # medium, everything
    python manage.py seed_dev --size large
    python manage.py seed_dev --size small --reset
    python manage.py seed_dev --only teams,tournaments
    python manage.py seed_dev --seed 42

The command is safe to rerun: every record is created with ``get_or_create``
against the seeder naming convention, so a second run refreshes existing rows
instead of duplicating them. ``--reset`` deletes the previously seeded rows
first.
"""

from __future__ import annotations

import os
import random
from contextlib import contextmanager

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models.signals import post_save

from accounts.models import RoleActivationCode, User
from devtools.seeders import scenarios as sc
from devtools.seeders.base import (
    DEFAULT_SEED,
    DEFAULT_SIZE,
    SEED_EMAIL_DOMAIN,
    SEED_MARK,
    SEED_NAME_PREFIX,
    SEED_PASSWORD,
    SIZES,
    SIZE_PROFILES,
    Rng,
)
from evaluation.models import JuryAssignment, LeaderboardEntry, SubmissionEvaluation
from news.models import NewsArticle
from notifications.models import (
    Notification,
    NotificationConfig,
    NotificationDeliveryTask,
    UserNotificationSettings,
)
from teams.models import Team, TeamInvitation, TeamJoinRequest, TeamMember
from tournaments.models import (
    Event,
    Round,
    Submission,
    Tournament,
    TournamentTeamRegistration,
)

AREAS = (
    'users',
    'teams',
    'tournaments',
    'rounds',
    'submissions',
    'evaluations',
    'news',
    'notifications',
    'calendar',
)

# Users, teams, tournaments, rounds, submissions, and evaluations are always
# built: every scenario in those areas depends on the ones before it, and the
# scenarios are meaningless if only half the chain exists. Restricting the seed
# to a subset only makes sense for the areas that stand on their own.
PREREQUISITE_AREAS = ('users', 'teams', 'tournaments', 'rounds', 'submissions', 'evaluations')
OPTIONAL_AREAS = ('news', 'notifications', 'calendar')


class Command(BaseCommand):
    help = 'Seed a development database with coherent, scenario-named test data.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--size',
            choices=SIZES,
            default=DEFAULT_SIZE,
            help=(
                'Dataset size. small = quick iteration, medium = everyday local '
                f'development (default), large = pagination and performance. '
                f'{SIZE_PROFILES["small"].describe}; {SIZE_PROFILES["medium"].describe}; '
                f'{SIZE_PROFILES["large"].describe}.'
            ),
        )
        parser.add_argument(
            '--seed', type=int, default=DEFAULT_SEED,
            help=f'Deterministic random seed (default: {DEFAULT_SEED}).',
        )
        parser.add_argument(
            '--only', default='',
            help=(
                'Comma-separated subset of areas to seed. Only the standalone '
                'areas (' + ', '.join(OPTIONAL_AREAS) + ') can be limited, '
                'because the rest (' + ', '.join(PREREQUISITE_AREAS) + ') are '
                'built as one coherent chain and are always created.'
            ),
        )
        parser.add_argument(
            '--reset', action='store_true',
            help='Delete previously seeded records before seeding again.',
        )
        parser.add_argument(
            '--force', action='store_true',
            help='Bypass the safety guard. Also requires ALLOW_SEED=1.',
        )

    # -------------------------------------------------------------- passwords

    @contextmanager
    def _fast_password_hashing(self):
        """Swap in the cheap hasher for the duration of the seed.

        Django's default hasher needs roughly 0.6 seconds per password, so a
        few hundred users means several minutes of pure hashing. The swap is
        scoped to this block and the configured hashers are restored on exit.
        """
        original = settings.PASSWORD_HASHERS
        settings.PASSWORD_HASHERS = ['devtools.seeders.base.SeedPasswordHasher']
        try:
            yield
        finally:
            settings.PASSWORD_HASHERS = original

    # ----------------------------------------------------------------- guard

    def _check_safety(self, *, force: bool) -> None:
        """Refuse to seed anything that is not plainly a development database."""
        if settings.DEBUG:
            return

        allowed = os.getenv('ALLOW_SEED', '') == '1'
        if force and allowed:
            return

        database = settings.DATABASES['default']
        engine = str(database.get('ENGINE', ''))
        name = str(database.get('NAME', ''))
        host = str(database.get('HOST') or '')

        is_sqlite = engine == 'django.db.backends.sqlite3'
        if not (is_sqlite and host in ('', 'localhost')) and not (allowed and force):
            raise CommandError(
                'Seeding refused: DEBUG is False and this does not look like a local '
                f'database (engine={engine!r}, host={host!r}). Set ALLOW_SEED=1 and pass '
                '--force to override.'
            )

        suspicious = any(token in name.lower() for token in ('prod', 'live', 'staging'))
        if suspicious and not (allowed and force):
            raise CommandError(
                f'Seeding refused: database name "{name}" looks like production. '
                'Set ALLOW_SEED=1 and pass --force to override.'
            )

        raise CommandError(
            'Seeding refused: DEBUG is False. This command is only for development. '
            'Set ALLOW_SEED=1 and pass --force to override.'
        )

    # -------------------------------------------------------------- signals

    def _disconnect_calendar_signals(self) -> list:
        """Detach the Google Calendar post_save receivers while seeding.

        Creating Events and Rounds fires ``sync_*_to_google_calendar``, which
        would attempt outbound API calls for every seeded row.
        """
        from tournaments.models import Event as EventModel
        from tournaments.models import Round as RoundModel
        from tournaments.signals import sync_event_to_google_calendar, sync_round_to_google_calendar

        disconnected = []
        for model, receiver in (
            (EventModel, sync_event_to_google_calendar),
            (RoundModel, sync_round_to_google_calendar),
        ):
            try:
                post_save.disconnect(receiver, sender=model)
                disconnected.append((receiver, model))
            except Exception:  # pragma: no cover - defensive
                pass
        return disconnected

    def _restore_signals(self, disconnected: list) -> None:
        for receiver, model in disconnected:
            try:
                post_save.connect(receiver, sender=model)
            except Exception:  # pragma: no cover - defensive
                pass

    # ---------------------------------------------------------------- reset

    def _reset_seeded_data(self) -> None:
        """Delete every record the seeder is responsible for."""
        self.stdout.write('Removing previously seeded data...')

        seeded_users = User.objects.filter(email__endswith=SEED_EMAIL_DOMAIN)

        with transaction.atomic():
            # Order matters only for readability; the FKs cascade on their own.
            Notification.objects.filter(recipient__email__endswith=SEED_EMAIL_DOMAIN).delete()
            NotificationDeliveryTask.objects.filter(recipient__email__endswith=SEED_EMAIL_DOMAIN).delete()
            NotificationConfig.objects.filter(user__email__endswith=SEED_EMAIL_DOMAIN).delete()
            UserNotificationSettings.objects.filter(user__email__endswith=SEED_EMAIL_DOMAIN).delete()

            NewsArticle.objects.filter(created_by__email__endswith=SEED_EMAIL_DOMAIN).delete()
            NewsArticle.objects.filter(title__contains=SEED_MARK).delete()

            LeaderboardEntry.objects.filter(team__name__contains=SEED_MARK).delete()
            LeaderboardEntry.objects.filter(
                tournament__name__icontains=SEED_NAME_PREFIX
            ).delete()

            SubmissionEvaluation.objects.filter(
                assignment__jury__email__endswith=SEED_EMAIL_DOMAIN
            ).delete()
            JuryAssignment.objects.filter(jury__email__endswith=SEED_EMAIL_DOMAIN).delete()
            JuryAssignment.objects.filter(
                submission__team__name__contains=SEED_MARK
            ).delete()

            Submission.objects.filter(team__name__contains=SEED_MARK).delete()
            Submission.objects.filter(team__name__icontains=SEED_NAME_PREFIX).delete()

            TournamentTeamRegistration.objects.filter(
                team__name__contains=SEED_MARK
            ).delete()
            TournamentTeamRegistration.objects.filter(
                team__name__icontains=SEED_NAME_PREFIX
            ).delete()

            Event.objects.filter(title__contains=SEED_MARK).delete()
            Event.objects.filter(title__icontains=SEED_NAME_PREFIX).delete()

            Round.objects.filter(name__contains=SEED_MARK).delete()
            Round.objects.filter(name__icontains=SEED_NAME_PREFIX).delete()

            Tournament.objects.filter(name__contains=SEED_MARK).delete()
            Tournament.objects.filter(name__icontains=SEED_NAME_PREFIX).delete()

            TeamJoinRequest.objects.filter(team__name__contains=SEED_MARK).delete()
            TeamJoinRequest.objects.filter(team__name__icontains=SEED_NAME_PREFIX).delete()
            TeamInvitation.objects.filter(team__name__contains=SEED_MARK).delete()
            TeamInvitation.objects.filter(team__name__icontains=SEED_NAME_PREFIX).delete()
            TeamMember.objects.filter(team__name__contains=SEED_MARK).delete()
            TeamMember.objects.filter(team__name__icontains=SEED_NAME_PREFIX).delete()
            Team.objects.filter(name__contains=SEED_MARK).delete()
            Team.objects.filter(name__icontains=SEED_NAME_PREFIX).delete()

            RoleActivationCode.objects.filter(code__icontains='SEED').delete()
            seeded_users.delete()

    # ------------------------------------------------------------ execution

    def handle(self, *args, **options):
        self._check_safety(force=options['force'])

        size = options['size']
        rng = Rng(options['seed'])
        random.seed(options['seed'])

        only = [item.strip() for item in (options['only'] or '').split(',') if item.strip()]
        unknown = [item for item in only if item not in AREAS]
        if unknown:
            raise CommandError(
                f'Unknown area(s): {", ".join(unknown)}. Valid areas: {", ".join(AREAS)}'
            )
        selected = set(only) if only else set(AREAS)

        # Outbound email must never leave the machine.
        if settings.EMAIL_BACKEND != 'django.core.mail.backends.locmem.EmailBackend':
            settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

        self.stdout.write(self.style.MIGRATE_HEADING(f'Seeding dev data (size={size}, seed={rng.seed})'))
        profile = SIZE_PROFILES[size]
        self.stdout.write(f'Bulk volume: {profile.describe}')

        if options['reset']:
            self._reset_seeded_data()

        disconnected = self._disconnect_calendar_signals()
        summary: dict[str, int] = {}
        notes: list[str] = []

        try:
            with self._fast_password_hashing(), transaction.atomic():
                users = sc.seed_users(rng)

                if 'users' in selected:
                    summary['users'] = len(users['jury']) + 4
                    notes.append(f'login roles: admin, organizer, 4 jury, captain, onboarder')
                    sc.seed_bulk_users(rng, profile.extra_users)
                    summary['users'] += profile.extra_users

                team_scenarios = sc.seed_teams(rng)
                competition = sc.seed_competition_teams(rng)

                if 'teams' in selected:
                    summary['teams'] = len(team_scenarios)
                    for label, info in team_scenarios.items():
                        notes.append(f'{label}: {info["note"]}')
                    sc.seed_bulk_teams(rng, profile.extra_teams)
                    summary['teams'] += profile.extra_teams

                tournaments = sc.seed_tournaments(users, competition)
                summary['tournaments'] = len(tournaments)
                sc.seed_bulk_tournaments(rng, profile.extra_tournaments, users)
                summary['tournaments'] += profile.extra_tournaments
                for name in tournaments:
                    notes.append(f'{name}: {tournaments[name].status}')

                rounds = sc.seed_running_rounds(rng, users, tournaments, competition)
                evaluated = sc.seed_evaluated_rounds(rng, users, tournaments, competition)
                all_rounds = {**rounds, **evaluated}
                summary['rounds'] = len(all_rounds)
                for name, round_obj in all_rounds.items():
                    notes.append(f'{name}: {round_obj.status}')

                if 'submissions' in selected:
                    summary['submissions'] = Submission.objects.filter(
                        round__name__contains=SEED_MARK
                    ).count()
                if 'evaluations' in selected:
                    summary['evaluations'] = SubmissionEvaluation.objects.filter(
                        assignment__submission__round__name__contains=SEED_MARK
                    ).count()
                    summary['leaderboards'] = LeaderboardEntry.objects.filter(
                        tournament__name__contains=SEED_MARK
                    ).count()

                if 'news' in selected:
                    summary['news'] = len(sc.seed_news(users))
                if 'notifications' in selected:
                    made = sc.seed_notifications(users)
                    summary['notifications'] = made['notifications']
                    summary['delivery_tasks'] = made['delivery_tasks']
                if 'calendar' in selected:
                    summary['calendar'] = sc.seed_calendar(tournaments)

        finally:
            self._restore_signals(disconnected)

        self._print_summary(summary, notes)
        self._print_accounts()

    # -------------------------------------------------------------- output

    def _print_summary(self, summary: dict, notes: list) -> None:
        self.stdout.write('')
        self.stdout.write(self.style.MIGRATE_HEADING('=== Seeded scenarios ==='))
        for note in notes:
            self.stdout.write(f'  - {note}')

        self.stdout.write('')
        self.stdout.write(self.style.MIGRATE_HEADING('=== Record summary ==='))
        header = f'{"Area":<22}{"Count":>8}'
        self.stdout.write(header)
        self.stdout.write('-' * len(header))
        for area, count in sorted(summary.items()):
            self.stdout.write(f'{area:<22}{count:>8}')
        self.stdout.write('-' * len(header))

    def _print_accounts(self) -> None:
        self.stdout.write('')
        self.stdout.write(self.style.MIGRATE_HEADING('=== Seed accounts ==='))
        header = f'{"Role":<12}{"Email":<40}{"Password":<14}Notes'
        self.stdout.write(header)
        self.stdout.write('-' * 78)

        accounts = list(
            User.objects.filter(email__endswith=SEED_EMAIL_DOMAIN)
            .order_by('-is_superuser', '-is_staff', 'id')
        )
        for user in accounts[:12]:
            notes = []
            if user.is_superuser:
                notes.append('superuser')
            elif user.is_staff:
                notes.append('staff')
            if user.needs_onboarding:
                notes.append('needs onboarding')
            label = ', '.join(notes)
            self.stdout.write(
                f'{user.role:<12}{user.email:<40}{SEED_PASSWORD:<14}{label}'
            )
        self.stdout.write('-' * 78)
        self.stdout.write(f'All seeded accounts share the password: {SEED_PASSWORD}')
        self.stdout.write(f'Emails use the domain {SEED_EMAIL_DOMAIN}')