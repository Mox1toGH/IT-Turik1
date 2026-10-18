"""Shared constants, sizing, and low-level factories for the dev seeder.

Scenario composition lives in :mod:`devtools.seeders.scenarios`; this module
only knows how to build individual, valid records.

Invariants enforced here rather than in scenarios:

* every write goes through ``full_clean()`` so model validation is never bypassed;
* all randomness comes from a seeded :class:`Rng`, never the global ``random``;
* every generated entity carries the seeder naming convention, which is what
  makes ``--reset`` able to find and delete seeded rows again.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.utils import timezone

from accounts.models import RoleActivationCode
from teams.models import Team, TeamInvitation, TeamJoinRequest, TeamMember
from tournaments.models import Icon, Round, Submission, Tournament, TournamentTeamRegistration

User = get_user_model()


class SeedPasswordHasher(PBKDF2PasswordHasher):
    """A deliberately cheap password hasher for seeded development accounts.

    Django's default PBKDF2 hasher costs roughly 0.6 seconds per hash, so
    seeding a few hundred users would otherwise take minutes. Seeding is
    development-only and every generated account shares the publicly documented
    password ``Test1234$``, so the hash strength buys nothing here.

    The command only installs this while seeding and restores the configured
    hashers immediately afterwards. It must never be used for real accounts.
    """

    algorithm = 'pbkdf2_sha256'
    iterations = 10_000

# --------------------------------------------------------------------------
# Naming convention -- this is the seeder-level "is this ours?" marker.
# No production model field was added for this purpose.
# --------------------------------------------------------------------------

SEED_EMAIL_DOMAIN = '@seed.local'
SEED_NAME_PREFIX = 'seed_'
SEED_PASSWORD = 'Test1234$'
SEED_MARK = ' — '

DEFAULT_SEED = 20240517

SIZES = ('small', 'medium', 'large')
DEFAULT_SIZE = 'medium'


@dataclass(frozen=True)
class SizeProfile:
    """Bulk volume per size.

    Scenario entities are identical at every size; only these three numbers
    grow. Bulk entities deliberately carry no workflow records, which keeps them
    valid under the participant-exclusivity rule regardless of size.
    """

    extra_users: int
    extra_teams: int
    extra_tournaments: int

    @property
    def describe(self) -> str:
        return (
            f'+{self.extra_users} users, +{self.extra_teams} teams, '
            f'+{self.extra_tournaments} tournaments'
        )


SIZE_PROFILES: dict[str, SizeProfile] = {
    'small': SizeProfile(extra_users=8, extra_teams=2, extra_tournaments=0),
    'medium': SizeProfile(extra_users=30, extra_teams=10, extra_tournaments=4),
    'large': SizeProfile(extra_users=120, extra_teams=45, extra_tournaments=15),
}


class Rng:
    """Deterministic random source, isolated from the global ``random``."""

    def __init__(self, seed: int) -> None:
        self._rng = random.Random(seed)
        self.seed = seed

    def pick(self, seq):
        return self._rng.choice(seq)

    def sample(self, seq, k: int):
        return self._rng.sample(list(seq), k)

    def shuffle(self, seq) -> None:
        self._rng.shuffle(seq)

    def randint(self, low: int, high: int) -> int:
        return self._rng.randint(low, high)

    def uniform(self, low: float, high: float) -> float:
        return self._rng.uniform(low, high)

    def random(self) -> float:
        return self._rng.random()


# --------------------------------------------------------------------------
# Naming helpers
# --------------------------------------------------------------------------

def scenario_name(subject: str, scenario: str) -> str:
    """Build a self-documenting name, e.g. ``Team — With Banned Members``."""
    return f'{subject}{SEED_MARK}{scenario}'


def seed_email(slug: str) -> str:
    return f'{slug}{SEED_EMAIL_DOMAIN}'


def bulk_name(subject: str, index: int) -> str:
    return f'{SEED_NAME_PREFIX}{subject} Bulk {index:03d}'


def bulk_email(slug: str, index: int) -> str:
    return f'{SEED_NAME_PREFIX}{slug}.{index:03d}{SEED_EMAIL_DOMAIN}'


def is_seeded_name(value: str) -> bool:
    return SEED_MARK in value or value.startswith(SEED_NAME_PREFIX)


def is_seeded_email(value: str) -> bool:
    return value.endswith(SEED_EMAIL_DOMAIN)


# --------------------------------------------------------------------------
# Users
# --------------------------------------------------------------------------

def make_user(
    *,
    username: str,
    email: str,
    full_name: str,
    role: str = 'team',
    password: str = SEED_PASSWORD,
    needs_onboarding: bool = False,
    city: str = '',
    is_staff: bool = False,
    is_superuser: bool = False,
):
    """Create a user, reusing an existing row with the same username.

    Hashing the password is the single most expensive thing this function can
    do, so it happens only when the row is new. On a rerun the stored hash
    already matches ``password`` and is left untouched.
    """
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'full_name': full_name,
            'role': role,
        },
    )
    changed_fields = []
    for field, value in (
        ('email', email),
        ('full_name', full_name),
        ('role', role),
        ('needs_onboarding', needs_onboarding),
        ('city', city),
        ('is_staff', is_staff),
        ('is_superuser', is_superuser),
        ('is_active', True),
    ):
        if getattr(user, field) != value:
            setattr(user, field, value)
            changed_fields.append(field)

    if created or not user.password:
        user.set_password(password)
        changed_fields.append('password')

    if changed_fields:
        user.save(update_fields=sorted(set(changed_fields)))
    return user


def make_role_activation_code(*, code: str, role: str, created_by, is_used: bool = False, used_by=None):
    obj, _ = RoleActivationCode.objects.get_or_create(
        code=code,
        defaults={'role': role, 'created_by': created_by},
    )
    if obj.is_used != is_used or obj.used_by_id != getattr(used_by, 'id', None):
        obj.is_used = is_used
        obj.used_by = used_by
        obj.used_at = timezone.now() if is_used else None
        obj.save()
    return obj


# --------------------------------------------------------------------------
# Teams and membership
# --------------------------------------------------------------------------

def make_team(
    *,
    name: str,
    email: str,
    captain,
    is_public: bool = True,
    organization: str = '',
    contact_telegram: str = '',
    contact_discord: str = '',
):
    team, _ = Team.objects.get_or_create(
        name=name,
        defaults={
            'email': email,
            'captain': captain,
            'is_public': is_public,
            'organization': organization,
            'contact_telegram': contact_telegram,
            'contact_discord': contact_discord,
        },
    )
    changed = False
    for field, value in (
        ('email', email),
        ('captain_id', captain.id),
        ('is_public', is_public),
        ('organization', organization),
        ('contact_telegram', contact_telegram),
        ('contact_discord', contact_discord),
    ):
        if getattr(team, field) != value:
            setattr(team, field, value)
            changed = True
    if changed:
        team.save()
    # The captain is always a member; teams/api.py does the same via get_or_create.
    add_member(team, captain)
    return team


def add_member(team, user) -> TeamMember:
    member, _ = TeamMember.objects.get_or_create(team=team, user=user)
    return member


def participant_ids(team) -> set[int]:
    """Mirrors ``tournaments.services.get_team_participant_ids``."""
    ids = set(TeamMember.objects.filter(team=team).values_list('user_id', flat=True))
    ids.add(team.captain_id)
    return ids


def make_invitation(*, team, user, invited_by, status: str, responded_at=None):
    """Create or re-point a (team, user) invitation.

    ``TeamInvitation`` is unique on (team, user); the API re-opens a previously
    responded invitation instead of inserting a second row, and so does this.
    """
    invitation = TeamInvitation.objects.filter(team=team, user=user).first()
    if invitation is None:
        invitation = TeamInvitation(team=team, user=user, invited_by=invited_by)
    invitation.status = status
    invitation.invited_by = invited_by
    invitation.responded_at = responded_at
    invitation.save()
    return invitation


def make_join_request(*, team, user, status: str, reviewed_by=None, reviewed_at=None):
    """Create or re-point a (team, user) join request. Unique on (team, user)."""
    join_request = TeamJoinRequest.objects.filter(team=team, user=user).first()
    if join_request is None:
        join_request = TeamJoinRequest(team=team, user=user)
    join_request.status = status
    join_request.reviewed_by = reviewed_by
    join_request.reviewed_at = reviewed_at
    join_request.save()
    return join_request


# --------------------------------------------------------------------------
# Tournaments, rounds, submissions, registrations
# --------------------------------------------------------------------------

def make_tournament(
    *,
    name: str,
    description: str,
    start_date,
    end_date,
    status: str,
    created_by,
    max_teams=None,
    min_team_members=None,
):
    tournament, _ = Tournament.objects.get_or_create(
        name=name,
        defaults={
            'description': description,
            'start_date': start_date,
            'end_date': end_date,
            'status': status,
            'created_by': created_by,
            'max_teams': max_teams,
            'min_team_members': min_team_members,
        },
    )
    changed = False
    for field, value in (
        ('description', description),
        ('start_date', start_date),
        ('end_date', end_date),
        ('status', status),
        ('created_by_id', getattr(created_by, 'id', None)),
        ('max_teams', max_teams),
        ('min_team_members', min_team_members),
    ):
        if getattr(tournament, field) != value:
            setattr(tournament, field, value)
            changed = True
    if changed:
        # Tournament.clean() enforces end_date > start_date and the >= 1 bounds.
        tournament.full_clean(exclude=['banner', 'created_at', 'updated_at'])
        tournament.save()
    return tournament


DEFAULT_CRITERIA = [
    {'id': 'crit_functionality', 'name': 'Functionality', 'description': 'Does the submission do what the brief asks?', 'max_score': 40},
    {'id': 'crit_code_quality', 'name': 'Code Quality', 'description': 'Readability, typing, and test coverage.', 'max_score': 30},
    {'id': 'crit_design', 'name': 'Design', 'description': 'Architecture and adherence to the brief.', 'max_score': 30},
]


def make_round(
    *,
    tournament,
    name: str,
    start_date,
    end_date,
    status: str,
    description: dict,
    tech_requirements: dict,
    must_have_requirements: dict,
    criteria=None,
    materials=None,
    passing_count=None,
    evaluation_criteria: str = Round.EVALUATION_SCORE,
):
    round_obj = Round.objects.filter(tournament=tournament, name=name).first()
    if round_obj is None:
        round_obj = Round(tournament=tournament, name=name)

    round_obj.start_date = start_date
    round_obj.end_date = end_date
    round_obj.status = status
    round_obj.description = description
    round_obj.tech_requirements = tech_requirements
    round_obj.must_have_requirements = must_have_requirements
    round_obj.criteria = criteria if criteria is not None else list(DEFAULT_CRITERIA)
    round_obj.materials = materials if materials is not None else []
    round_obj.passing_count = passing_count
    round_obj.evaluation_criteria = evaluation_criteria

    # Round.clean() enforces: ordering, containment in the tournament window,
    # no overlap with sibling rounds, one active round, and criteria shape.
    # Cross-model uniqueness (one active round per tournament) is a DB
    # constraint, so siblings are validated explicitly here.
    #
    # These querysets must be evaluated *before* save(): a lazy queryset would
    # otherwise be re-evaluated afterwards and match the row we just inserted.
    siblings = Round.objects.filter(tournament=tournament).exclude(pk=round_obj.pk)
    overlapping = list(
        siblings.filter(
            start_date__lt=round_obj.end_date, end_date__gt=round_obj.start_date
        ).values_list('name', flat=True)
    )
    active_siblings = list(
        siblings.filter(status=Round.STATUS_ACTIVE).values_list('name', flat=True)
    )

    if round_obj.status == Round.STATUS_ACTIVE and active_siblings:
        raise ValueError(
            f'Cannot seed round "{name}" as active: '
            f'{active_siblings[0]} is already active in this tournament.'
        )

    round_obj.full_clean(exclude=['banner'])
    if overlapping:
        raise ValueError(f'Round "{name}" overlaps {overlapping[0]}')
    round_obj.save()
    return round_obj


def make_registration(*, tournament, team, created_by=None, is_active: bool = True, is_disqualified: bool = False, disqualification_reason=None):
    """Create the (tournament, team) registration, which is unique together."""
    registration = TournamentTeamRegistration.objects.filter(tournament=tournament, team=team).first()
    if registration is None:
        registration = TournamentTeamRegistration(tournament=tournament, team=team)
    registration.created_by = created_by or team.captain
    registration.is_active = is_active
    registration.is_disqualified = is_disqualified
    registration.disqualification_reason = disqualification_reason
    registration.save()
    return registration


def make_submission(
    *,
    team,
    round_obj,
    github_url: str,
    demo_video_url: str = '',
    live_demo_url: str = '',
    description: str = '',
):
    """Create the (team, round) submission.

    ``Submission.clean()`` requires an active round and the team captain as
    ``created_by``, so both are derived here rather than passed in.
    """
    submission = Submission.objects.filter(team=team, round=round_obj).first()
    if submission is None:
        submission = Submission(team=team, round=round_obj)
    submission.github_url = github_url
    submission.demo_video_url = demo_video_url
    submission.live_demo_url = live_demo_url
    submission.description = description
    submission.created_by = team.captain
    submission.full_clean(exclude=['demo_video_file'])
    submission.save()
    return submission


# --------------------------------------------------------------------------
# Calendar
# --------------------------------------------------------------------------

def get_or_create_icon(name: str, path: str) -> Icon:
    icon, _ = Icon.objects.get_or_create(name=name, defaults={'path': path})
    return icon


# --------------------------------------------------------------------------
# Time helpers
# --------------------------------------------------------------------------

def hours(count: int):
    return timedelta(hours=count)


def days(count: int):
    return timedelta(days=count)


def now():
    return timezone.now()