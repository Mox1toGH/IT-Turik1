"""Scenario builders for the development seeder.

Each function below creates one recognisable application state and names every
record after it, so a developer can find the scenario by reading names alone.
The same set runs at every size; only bulk volume differs (see ``base.SIZE_PROFILES``).

Business rules are respected rather than bypassed:

* a team and all of its members may take part in only one tournament that is
  ``registration`` or ``running`` at a time, so each competitor team belongs to
  exactly one active scenario tournament;
* round state transitions go through the real services in ``tournaments.services``,
  which means a tournament only reaches ``running`` / ``finished`` by actually
  being driven through the documented lifecycle;
* submissions exist only for ``active`` rounds and are created by the captain,
  because ``Submission.clean()`` enforces both.
"""

from __future__ import annotations

from collections import OrderedDict

from django.db import transaction

from evaluation.leaderboard_service import save_leaderboard_snapshot
from evaluation.models import JuryAssignment, SubmissionEvaluation
from evaluation.services import apply_passing_count
from news.models import NewsArticle
from notifications.config import EVENTS as NOTIFICATION_EVENTS
from notifications.models import Notification, NotificationDeliveryTask
from tournaments.models import Event, Round, Tournament
from tournaments.services import start_round

from . import tiptap
from .base import (
    Rng,
    add_member,
    bulk_email,
    bulk_name,
    days,
    get_or_create_icon,
    make_invitation,
    make_join_request,
    make_registration,
    make_role_activation_code,
    make_round,
    make_submission,
    make_team,
    make_tournament,
    make_user,
    now,
    scenario_name,
    seed_email,
)

FIRST_NAMES = [
    'Anna', 'Bohdan', 'Cyril', 'Daria', 'Eduard', 'Flora', 'Hryhoriy', 'Iryna',
    'Kostiantyn', 'Liubov', 'Maksym', 'Nataliia', 'Oleksandr', 'Polina', 'Roman',
    'Sofia', 'Taras', 'Valeriia', 'Yaroslav', 'Zoriana',
]
LAST_NAMES = [
    'Bondar', 'Chernenko', 'Datsenko', 'Fedorova', 'Hrytsenko', 'Ivanova',
    'Kravets', 'Lytvyn', 'Moroz', 'Nechiporuk', 'Oliynyk', 'Pavlenko',
    'Rusnak', 'Savchenko', 'Tkachuk', 'Us', 'Vasylenko', 'Wirth', 'Yaremchuk', 'Zelinka',
]
CITIES = ['Kyiv', 'Lviv', 'Odesa', 'Kharkiv', 'Dnipro', 'Vinnytsia', 'Ivano-Frankivsk']

PY_STACK = ['Python 3.12', 'Django 5.2', 'PostgreSQL 16']


def _person(rng: Rng) -> str:
    return f'{rng.pick(FIRST_NAMES)} {rng.pick(LAST_NAMES)}'


def _rich_round_fields(*, label: str, tournament_name: str, focus: str, stack) -> tuple[dict, dict, dict]:
    return (
        tiptap.round_task_description(round_label=label, tournament_name=tournament_name, focus=focus),
        tiptap.round_tech_requirements(stack=stack, focus=focus),
        tiptap.round_must_have_requirements(
            checks=[
                'The project builds from a clean checkout with one documented command.',
                'Every public endpoint is documented in the README.',
                'The core logic is covered by automated tests.',
            ],
            penalty_note=(
                'A submission missing any must-have item scores zero for the round, '
                'no matter how good the implementation is.'
            ),
        ),
    )


def _github_slug(name: str) -> str:
    head = name.split('—')[0].strip().lower()
    slug = '-'.join(head.split())
    return ''.join(ch for ch in slug if ch.isalnum() or ch == '-') or 'seed-team'


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def seed_users(rng: Rng) -> dict:
    """Platform roles plus a pool of ordinary participants."""
    admin = make_user(
        username='seed_admin', email=seed_email('admin'),
        full_name='Seed Admin', role='admin', city='Kyiv',
        is_staff=True, is_superuser=True,
    )
    organizer = make_user(
        username='seed_organizer', email=seed_email('organizer'),
        full_name='Seed Organizer', role='organizer', city='Lviv',
    )
    jury = [
        make_user(
            username=f'seed_jury_{index:02d}', email=seed_email(f'jury.{index:02d}'),
            full_name=f'{FIRST_NAMES[index - 1]} {LAST_NAMES[index]}',
            role='jury', city=rng.pick(CITIES),
        )
        for index in range(1, 5)
    ]
    captain = make_user(
        username='seed_captain', email=seed_email('captain'),
        full_name='Seed Team Captain', role='team', city='Odesa',
    )
    onboarder = make_user(
        username='seed_onboarding', email=seed_email('onboarding'),
        full_name='Seed Half Registered', role='team', city='Kharkiv',
        needs_onboarding=True,
    )

    make_role_activation_code(code='SEED-ORGANIZER-01', role='organizer', created_by=admin)
    make_role_activation_code(code='SEED-JURY-01', role='jury', created_by=admin, is_used=True, used_by=jury[0])

    return {
        'admin': admin, 'organizer': organizer, 'jury': jury,
        'captain': captain, 'onboarder': onboarder,
    }


def seed_bulk_users(rng: Rng, count: int) -> list:
    """Filler participants. Carried no workflow records of any kind."""
    created = []
    for offset in range(count):
        index = 100 + offset
        created.append(make_user(
            username=f'seed_bulk_user_{index:03d}',
            email=bulk_email('bulkuser', index),
            full_name=_person(rng), role='team', city=rng.pick(CITIES),
        ))
    return created


def seed_bulk_teams(rng: Rng, count: int) -> list:
    """Standalone teams with no invitations, requests, or registrations.

    Safe at any size: because they never register for a ``registration`` or
    ``running`` tournament, they cannot violate participant exclusivity.
    """
    teams = []
    for offset in range(count):
        index = 200 + offset
        captain = make_user(
            username=f'seed_bulkcap_{index:03d}', email=bulk_email('bulkcap', index),
            full_name=_person(rng), role='team', city=rng.pick(CITIES),
        )
        # Roster size is derived from the index rather than the rng, so seeding a
        # larger size later never adds or removes members from an existing team.
        extra_members = 1 + (index % 4)
        roster = [captain] + [
            make_user(
                username=f'seed_bulkmem_{index:03d}_{slot}',
                email=bulk_email('bulkmem', index * 10 + slot),
                full_name=_person(rng), role='team', city=rng.pick(CITIES),
            )
            for slot in range(extra_members)
        ]
        team = make_team(
            name=bulk_name('Team', offset + 1),
            email=bulk_email('bulkteam', index),
            captain=captain,
            is_public=True,
            organization=f'Seed Org {rng.randint(1, 12)}',
            contact_telegram=f'seed_bulk_{index:03d}',
        )
        for member in roster[1:]:
            add_member(team, member)
        teams.append(team)
    return teams


def seed_bulk_tournaments(rng: Rng, count: int, users: dict) -> list:
    """Long-name tournaments with zero rounds, for pagination and filtering."""
    tournaments = []
    for offset in range(count):
        index = 300 + offset
        start = now() + days(20 + index % 40)
        tournaments.append(make_tournament(
            name=bulk_name('Tournament', offset + 1),
            description=(
                f'Bulk tournament {index:03d}, created to exercise pagination, search, and '
                'filtering. It has no rounds and no registrations on purpose, so it stays '
                'a stable list fixture that never interferes with the scenario tournaments.'
            ),
            start_date=start,
            end_date=start + days(3),
            status='draft',
            created_by=users['organizer'] if offset % 2 == 0 else users['admin'],
            max_teams=None,
            min_team_members=None,
        ))
    return tournaments


# ---------------------------------------------------------------------------
# Teams: membership / invitation / join-request scenarios
# ---------------------------------------------------------------------------

def seed_teams(rng: Rng) -> 'OrderedDict[str, dict]':
    scenarios: OrderedDict[str, dict] = OrderedDict()
    counter = {'n': 0}

    def person(suffix: str, name: str | None = None):
        counter['n'] += 1
        return make_user(
            username=f'seed_{suffix}_{counter["n"]:02d}',
            email=seed_email(f'{suffix}.{counter["n"]:02d}'),
            full_name=name or _person(rng), role='team', city=rng.pick(CITIES),
        )

    def team_for(scenario: str, *, is_public: bool = True):
        captain = person('cap', 'Seed Captain')
        team = make_team(
            name=scenario_name('Team', scenario),
            email=seed_email('team.' + scenario.lower().replace(' ', '.').replace('(', '').replace(')', '')),
            captain=captain,
            is_public=is_public,
            organization=f'Seed Org {rng.randint(1, 20)}',
            contact_telegram=f'seed_t{rng.randint(10000, 99999)}',
        )
        return captain, team

    # T1
    captain, team = team_for('Captain Only (No Members Yet)')
    scenarios['Team — Captain Only (No Members Yet)'] = {
        'team': team,
        'note': 'Captain only. Fails any min_team_members check and shows the empty roster UI.',
    }

    # T2
    captain, team = team_for('Full Active Roster')
    for _ in range(3):
        add_member(team, person('roster'))
    scenarios['Team — Full Active Roster'] = {
        'team': team,
        'note': 'Four active members including the captain.',
    }

    # T3
    captain, team = team_for('Pending Invitation')
    make_invitation(
        team=team, user=person('invitee', 'Seed Invitee Awaiting Reply'),
        invited_by=captain, status='invited',
    )
    scenarios['Team — Pending Invitation'] = {
        'team': team,
        'note': 'Invitation status=invited with responded_at=NULL. Actionable in the recipient inbox.',
    }

    # T4 -- teams/api.py always writes the TeamMember row alongside an accepted
    # invitation, so both are seeded together to stay faithful.
    captain, team = team_for('Accepted Invitation')
    joiner = person('accepted', 'Seed Accepted Invitee')
    make_invitation(team=team, user=joiner, invited_by=captain, status='accepted', responded_at=now() - days(2))
    add_member(team, joiner)
    scenarios['Team — Accepted Invitation'] = {
        'team': team,
        'note': 'Invitation status=accepted, responded_at set, and a matching TeamMember row.',
    }

    # T5
    captain, team = team_for('Declined Invitation')
    make_invitation(
        team=team, user=person('declined', 'Seed Declined Invitee'),
        invited_by=captain, status='declined', responded_at=now() - days(3),
    )
    scenarios['Team — Declined Invitation'] = {
        'team': team,
        'note': 'Invitation status=declined and deliberately no TeamMember row.',
    }

    # T6 -- join requests are only possible against a public team.
    captain, team = team_for('Pending Join Requests', is_public=True)
    for _ in range(2):
        make_join_request(team=team, user=person('applicant'), status='pending')
    scenarios['Team — Pending Join Requests'] = {
        'team': team,
        'note': 'Two pending join requests awaiting captain review.',
    }

    # T7
    captain, team = team_for('Accepted Join Request', is_public=True)
    applicant = person('approved', 'Seed Approved Applicant')
    make_join_request(
        team=team, user=applicant, status='accepted',
        reviewed_by=captain, reviewed_at=now() - days(4),
    )
    add_member(team, applicant)
    scenarios['Team — Accepted Join Request'] = {
        'team': team,
        'note': 'Join request status=accepted with reviewer and timestamp, plus membership.',
    }

    # T8
    captain, team = team_for('Declined Join Request', is_public=True)
    make_join_request(
        team=team, user=person('rejected', 'Seed Rejected Applicant'), status='declined',
        reviewed_by=captain, reviewed_at=now() - days(5),
    )
    scenarios['Team — Declined Join Request'] = {
        'team': team,
        'note': 'Join request status=declined, reviewer recorded, no TeamMember row.',
    }

    # T9
    _, team = team_for('Private (Hidden From List)', is_public=False)
    scenarios['Team — Private (Hidden From List)'] = {
        'team': team,
        'note': 'is_public=False, so the team is filtered out of the public team list.',
    }

    return scenarios


def seed_competition_teams(rng: Rng) -> 'OrderedDict[str, dict]':
    """Teams that compete in the tournament scenarios.

    Each key is used by exactly one tournament, which is what keeps the
    participant-exclusivity rule intact.
    """
    teams: OrderedDict[str, dict] = OrderedDict()
    counter = {'n': 0}

    def competitor(key: str):
        counter['n'] += 1
        return make_user(
            username=f'seed_comp_{key.replace(".", "_")}_{counter["n"]:02d}',
            email=seed_email('comp.' + key + f'.{counter["n"]:02d}'),
            full_name=_person(rng), role='team', city=rng.pick(CITIES),
        )

    def entry(key: str, label: str, size: int):
        captain = competitor(key)
        team = make_team(
            name=scenario_name('Team', label),
            email=seed_email('reg.' + key.replace('.', '-')),
            captain=captain,
            is_public=True,
            organization=f'Seed Org {rng.randint(1, 20)}',
        )
        for _ in range(size - 1):
            add_member(team, competitor(key))
        teams[key] = {'team': team, 'label': label}
        return team

    for index, label in enumerate(('Alpha', 'Beta', 'Gamma', 'Delta')):
        entry(f'open.{index}', f'{label} (Open Registration)', 3)
    for index, label in enumerate(('North', 'South', 'East')):
        entry(f'full.{index}', f'{label} (Full Tournament)', 2)
    for index, label in enumerate(('Pioneer', 'Quantum', 'Nimbus', 'Outrider')):
        entry(f'running.{index}', f'{label} (Running Tournament)', 3)
    for index, label in enumerate(('Summit', 'Forge', 'Basalt')):
        entry(f'cancelled.{index}', f'{label} (Cancelled Registration)', 3)
    for index, label in enumerate(('Atlas', 'Vertex', 'Quartz', 'Meridian')):
        entry(f'finished.{index}', f'{label} (Finished Tournament)', 3)

    return teams


# ---------------------------------------------------------------------------
# Tournaments
# ---------------------------------------------------------------------------

def seed_tournaments(users: dict, teams: OrderedDict) -> OrderedDict:
    """Create the scenario tournaments in ``registration`` or ``draft``.

    None of these is created directly as ``running`` or ``finished``: those
    statuses are reached only by driving the real round lifecycle in
    ``seed_evaluated_rounds`` / ``seed_running_rounds``.
    """
    admin, organizer = users['admin'], users['organizer']
    tournaments: OrderedDict = OrderedDict()

    # --- R1: registration open, nobody registered yet.
    start = now() + days(5)
    tournaments['Tournament — No Registrations Yet'] = make_tournament(
        name=scenario_name('Tournament', 'No Registrations Yet'),
        description=(
            'Registration is open but no team has signed up yet. Use this tournament '
            'to inspect the empty-state copy of the registration screen.'
        ),
        start_date=start, end_date=start + days(21),
        status='registration', created_by=organizer, max_teams=16, min_team_members=2,
    )

    # --- R2: registration open with a genuinely mixed pool of states.
    start = now() + days(3)
    mixed = make_tournament(
        name=scenario_name('Tournament', 'Mixed Registration States'),
        description=(
            'Registration is open with four teams in different states: two active, one '
            'withdrawn, one disqualified. Inspect the team list tabs and the eligibility '
            'reasons shown on the register-team screen. It also carries a future round '
            'that has not been started.'
        ),
        start_date=start, end_date=start + days(28),
        status='registration', created_by=organizer, max_teams=8, min_team_members=2,
    )
    for key in ('open.0', 'open.1'):
        team = teams[key]['team']
        make_registration(tournament=mixed, team=team, created_by=team.captain, is_active=True)
    withdrawn = teams['open.2']['team']
    make_registration(tournament=mixed, team=withdrawn, created_by=withdrawn.captain, is_active=False)
    outrider = teams['open.3']['team']
    make_registration(
        tournament=mixed, team=outrider, created_by=outrider.captain,
        is_active=False, is_disqualified=True,
        disqualification_reason='Disqualified during registration: the member roster was incomplete.',
    )
    tournaments['Tournament — Mixed Registration States'] = mixed

    # --- R3: registration open and already at max_teams.
    start = now() + days(7)
    full = make_tournament(
        name=scenario_name('Tournament', 'Full At Max Teams'),
        description=(
            'Three teams are registered and max_teams is 3, so the register-team screen '
            'reports that the registration limit has been reached.'
        ),
        start_date=start, end_date=start + days(14),
        status='registration', created_by=admin, max_teams=3, min_team_members=2,
    )
    for key in ('full.0', 'full.1', 'full.2'):
        team = teams[key]['team']
        make_registration(tournament=full, team=team, created_by=team.captain, is_active=True)
    tournaments['Tournament — Full At Max Teams'] = full

    # --- R4: will become running (disqualified participant).
    start = now() - days(10)
    running = make_tournament(
        name=scenario_name('Tournament', 'Running With Disqualified Team'),
        description=(
            'The tournament is running. One team was disqualified by an admin for '
            'submitting somebody else\'s code, so it appears under the disqualified tab '
            'and is excluded from the leaderboard.'
        ),
        start_date=start, end_date=start + days(30),
        status='registration', created_by=organizer, max_teams=8, min_team_members=3,
    )
    for key in ('running.0', 'running.1', 'running.2'):
        team = teams[key]['team']
        make_registration(tournament=running, team=team, created_by=team.captain, is_active=True)
    disqualified = teams['running.3']['team']
    make_registration(
        tournament=running, team=disqualified, created_by=disqualified.captain,
        is_active=False, is_disqualified=True,
        disqualification_reason='Disqualified: the repository contains a solution copied from another team.',
    )
    tournaments['Tournament — Running With Disqualified Team'] = running

    # --- R5: will become running (cancelled registration).
    start = now() - days(5)
    cancelled = make_tournament(
        name=scenario_name('Tournament', 'Running With Cancelled Registration'),
        description=(
            'The tournament is running and one team cancelled its registration before '
            'submitting anything. Compare it with the disqualified team in the other '
            'running tournament: both registrations are inactive, but this one was not '
            'disqualified. Its round closed for submissions and the jury is still scoring.'
        ),
        start_date=start, end_date=start + days(25),
        status='registration', created_by=organizer, max_teams=8, min_team_members=3,
    )
    for key in ('cancelled.0', 'cancelled.1'):
        team = teams[key]['team']
        make_registration(tournament=cancelled, team=team, created_by=team.captain, is_active=True)
    dropped = teams['cancelled.2']['team']
    make_registration(tournament=cancelled, team=dropped, created_by=dropped.captain, is_active=False)
    tournaments['Tournament — Running With Cancelled Registration'] = cancelled

    # --- R6: will finish after two evaluated rounds.
    start = now() - days(45)
    finished = make_tournament(
        name=scenario_name('Tournament', 'Finished With Final Standings'),
        description=(
            'A completed tournament with two evaluated rounds, a rank-based elimination '
            'after round one, and a final leaderboard. Use it to inspect the archive view '
            'and the standings screens.'
        ),
        start_date=start, end_date=start + days(40),
        status='registration', created_by=admin, max_teams=8, min_team_members=3,
    )
    for key in ('finished.0', 'finished.1', 'finished.2', 'finished.3'):
        team = teams[key]['team']
        make_registration(tournament=finished, team=team, created_by=team.captain, is_active=True)
    tournaments['Tournament — Finished With Final Standings'] = finished

    # --- R7: draft, no rounds.
    start = now() + days(30)
    tournaments['Tournament — Draft Without Rounds'] = make_tournament(
        name=scenario_name('Tournament', 'Draft Without Rounds'),
        description=(
            'A draft tournament that has not been opened for registration and has no '
            'rounds. Inspect the draft-state copy and the "add the first round" empty state.'
        ),
        start_date=start, end_date=start + days(60),
        status='draft', created_by=organizer, max_teams=None, min_team_members=None,
    )

    return tournaments


# ---------------------------------------------------------------------------
# Rounds and the lifecycle
# ---------------------------------------------------------------------------

@transaction.atomic
def seed_running_rounds(rng: Rng, users: dict, tournaments: OrderedDict, teams: OrderedDict) -> OrderedDict:
    """Activate one round on each running tournament.

    ``start_round`` is the real service, so it flips the tournament from
    ``registration`` to ``running`` and refuses to run if the prerequisites in
    ``tournaments.services`` are not met.
    """
    rounds: OrderedDict = OrderedDict()

    # Round A -- active, with submissions in progress.
    running = tournaments['Tournament — Running With Disqualified Team']
    description, tech, must = _rich_round_fields(
        label='Round 1 — Submissions Open',
        tournament_name=running.name,
        focus='task scheduling service',
        stack=PY_STACK,
    )
    round_a = make_round(
        tournament=running,
        name=scenario_name('Round', 'Submissions Open (Active)'),
        start_date=now() - days(2), end_date=now() + days(5),
        status='draft',
        description=description, tech_requirements=tech, must_have_requirements=must,
        materials=[
            {'title': 'Starter repository', 'url': 'https://github.com/seed/starter'},
            {'title': 'API reference', 'url': 'https://docs.example.invalid/api'},
        ],
        passing_count=None,
    )
    start_round(round_a)
    round_a.refresh_from_db()
    rounds['Round — Submissions Open (Active)'] = round_a

    # Submissions may only be created while the round is active.
    for key in ('running.0', 'running.1', 'running.2'):
        team = teams[key]['team']
        make_submission(
            team=team, round_obj=round_a,
            github_url=f'https://github.com/seed/{_github_slug(team.name)}/round-1',
            demo_video_url=f'https://www.youtube.com/watch?v=running{team.id}',
            live_demo_url=f'https://demo.seed.invalid/r1/{team.id}',
            description=(
                f'Submission from {team.name} for {round_a.name}. The demo walks through '
                'the happy path first and then the error handling.'
            ),
        )

    # Assign jury but leave every submission unscored: this is the
    # "jury is working" state.
    for submission in round_a.submissions.all():
        for jury_member in users['jury'][:2]:
            JuryAssignment.objects.get_or_create(submission=submission, jury=jury_member)

    # Round B -- submissions are closed and the jury is still working through
    # them, so this round shows the "awaiting evaluation" state.
    #
    # Like the historical rounds below, this one is stepped through the state
    # machine by writing the status directly: start_round() refuses a round whose
    # deadline has passed, and by definition this round's deadline has passed.
    cancelled = tournaments['Tournament — Running With Cancelled Registration']
    description, tech, must = _rich_round_fields(
        label='Round 1 — In Evaluation',
        tournament_name=cancelled.name,
        focus='realtime leaderboard broadcast',
        stack=['Python 3.12', 'Channels 4.2'],
    )
    round_b = make_round(
        tournament=cancelled,
        name=scenario_name('Round', 'In Evaluation (Submission Closed)'),
        start_date=cancelled.start_date, end_date=now() - days(1),
        status='draft',
        description=description, tech_requirements=tech, must_have_requirements=must,
        passing_count=2,
    )

    def set_status(round_obj, status: str) -> None:
        round_obj.status = status
        round_obj.save(update_fields=['status', 'updated_at'])

    set_status(round_b, Round.STATUS_ACTIVE)
    for key in ('cancelled.0', 'cancelled.1'):
        team = teams[key]['team']
        make_submission(
            team=team, round_obj=round_b,
            github_url=f'https://github.com/seed/{_github_slug(team.name)}/round-1',
            demo_video_url=f'https://www.youtube.com/watch?v=eval{team.id}',
            description=(
                f'Submission from {team.name} for {round_b.name}. Submissions are '
                'closed for this round and the jury is still scoring.'
            ),
        )
        submission = team.submissions.get(round=round_b)
        for jury_member in users['jury'][:3]:
            assignment, _ = JuryAssignment.objects.get_or_create(
                submission=submission, jury=jury_member,
            )
            # Deliberately leave one jury member unevaluated so the round reads
            # as "evaluation in progress" rather than finished.
            if jury_member.id != users['jury'][2].id:
                _score_evaluation(
                    rng=rng, assignment=assignment,
                    criteria=round_b.criteria, jury_member=jury_member,
                )
    set_status(round_b, Round.STATUS_SUBMISSION_CLOSED)

    # The round is no longer active, so the tournament is running without a
    # live round. This is the state the app reaches after a deadline passes.
    cancelled.status = Tournament.STATUS_RUNNING
    cancelled.save(update_fields=['status', 'updated_at'])
    cancelled.refresh_from_db()
    round_b.refresh_from_db()
    rounds['Round — In Evaluation (Submission Closed)'] = round_b

    # Round C -- still draft, scheduled in the future.
    mixed = tournaments['Tournament — Mixed Registration States']
    description, tech, must = _rich_round_fields(
        label='Round 1 — Not Started',
        tournament_name=mixed.name,
        focus='role activation flow',
        stack=['Python 3.12', 'Django 5.2'],
    )
    rounds['Round — Not Started (Draft)'] = make_round(
        tournament=mixed,
        name=scenario_name('Round', 'Not Started (Draft)'),
        start_date=now() + days(10), end_date=now() + days(25),
        status='draft',
        description=description, tech_requirements=tech, must_have_requirements=must,
        passing_count=None,
    )

    return rounds


@transaction.atomic
def seed_evaluated_rounds(rng: Rng, users: dict, tournaments: OrderedDict, teams: OrderedDict) -> OrderedDict:
    """Build a finished tournament with two evaluated rounds.

    A note on how the lifecycle is driven here. ``tournaments.services.start_round``
    deliberately refuses a round whose deadline has already passed, so a
    tournament that ended weeks ago cannot be replayed through the live services.
    The rounds below are therefore stepped through the same state machine
    (``draft -> active -> submission_closed -> evaluated``) by writing the status
    directly.

    Everything that is *derived* from those states is still produced by the real
    production functions, so no result is invented:
    ``SubmissionEvaluation.save`` computes the scores, ``apply_passing_count``
    performs rank-based elimination, and ``save_leaderboard_snapshot`` writes the
    round and final-tournament standings.
    """
    finished = tournaments['Tournament — Finished With Final Standings']
    jury = users['jury'][:3]
    rounds: OrderedDict = OrderedDict()

    def still_playing() -> list:
        return [
            entry['team'] for entry in teams.values()
            if entry['team'].tournament_registrations.filter(
                tournament=finished, is_active=True
            ).exists()
        ]

    def set_status(round_obj, status: str) -> None:
        round_obj.status = status
        round_obj.save(update_fields=['status', 'updated_at'])

    last_round = None
    for index, (label, passing_count, focus) in enumerate((
        ('Evaluated (Rank Elimination)', 2, 'leaderboard computation'),
        ('Evaluated (Final Standings)', None, 'final reporting'),
    ), start=1):
        round_start = finished.start_date + days(index * 14)
        round_end = round_start + days(10)
        description, tech, must = _rich_round_fields(
            label=f'Round {index} — {label}',
            tournament_name=finished.name,
            focus=focus,
            stack=['Python 3.12', 'Django 5.2', 'pytest'],
        )
        round_obj = make_round(
            tournament=finished,
            name=scenario_name('Round', label),
            start_date=round_start, end_date=round_end,
            status='draft',
            description=description, tech_requirements=tech, must_have_requirements=must,
            passing_count=passing_count,
        )

        # draft -> active. Submissions are only valid on an active round.
        set_status(round_obj, Round.STATUS_ACTIVE)
        for team in still_playing():
            make_submission(
                team=team, round_obj=round_obj,
                github_url=f'https://github.com/seed/{_github_slug(team.name)}/round-{index}',
                demo_video_url=f'https://www.youtube.com/watch?v=finished{index}{team.id}',
                live_demo_url=f'https://demo.seed.invalid/rf{index}/{team.id}',
                description=(
                    f'Submission from {team.name} for {round_obj.name}. See the README '
                    'for the architecture decisions and the demo for the behaviour.'
                ),
            )
            submission = team.submissions.get(round=round_obj)
            for jury_member in jury:
                assignment, _ = JuryAssignment.objects.get_or_create(
                    submission=submission, jury=jury_member,
                )
                _score_evaluation(
                    rng=rng, assignment=assignment,
                    criteria=round_obj.criteria, jury_member=jury_member,
                )

        # active -> submission_closed -> evaluated
        set_status(round_obj, Round.STATUS_SUBMISSION_CLOSED)
        set_status(round_obj, Round.STATUS_EVALUATED)

        # Real elimination logic: deactivates the teams ranked below passing_count.
        apply_passing_count(round_obj)

        round_obj.refresh_from_db()
        rounds[round_obj.name] = round_obj
        last_round = round_obj

    # All rounds evaluated, so the tournament is finished. The leaderboard service
    # writes both the per-round entries and the tournament-level standings that
    # the archive view reads.
    finished.status = Tournament.STATUS_FINISHED
    finished.save(update_fields=['status', 'updated_at'])
    finished.refresh_from_db()
    save_leaderboard_snapshot(tournament_id=finished.id, round_id=last_round.id)

    return rounds


def _score_evaluation(*, rng: Rng, assignment, criteria, jury_member):
    """Create the OneToOne evaluation; its save() derives total and final score."""
    if SubmissionEvaluation.objects.filter(assignment=assignment).exists():
        return None
    scores = []
    for criterion in criteria:
        max_score = criterion['max_score']
        scores.append({
            'criterion_id': criterion['id'],
            'criterion_name': criterion['name'],
            'score': rng.randint(max(1, int(max_score * 0.4)), int(max_score)),
        })
    return SubmissionEvaluation.objects.create(
        assignment=assignment,
        scores=scores,
        comment=f'Evaluation by {jury_member.full_name}: solid submission, notes in the demo.',
    )


# ---------------------------------------------------------------------------
# News, notifications, calendar
# ---------------------------------------------------------------------------

def _make_article(author, content, *, title: str):
    article, _ = NewsArticle.objects.get_or_create(
        title=title, defaults={'content': content, 'created_by': author},
    )
    if article.content != content or article.created_by_id != author.id:
        article.content = content
        article.created_by = author
        article.full_clean()
        article.save()
    return article


def seed_news(users: dict) -> list:
    admin, organizer = users['admin'], users['organizer']
    return [
        _make_article(admin, tiptap.news_article_content(
            headline='Welcome to the platform',
            standfirst='Everything you need to know to run your first tournament here.',
            sections=[
                ('Create the tournament', 'Set a name, a description, and the dates. Keep the status as draft until the schedule is final.'),
                ('Open registration', 'Move the tournament to registration so teams can sign up. Teams must meet the minimum member count you set.'),
                ('Publish rounds', 'Add one round per task. Every round carries its own brief, requirements, and scoring criteria.'),
            ],
        ), title=scenario_name('News', 'Welcome Guide (Structured Content)')),

        _make_article(organizer, tiptap.news_feature_content(
            headline='Feature Showcase (Every Node And Mark)',
            blocks=[
                tiptap.para(tiptap.text(
                    'The article below covers the whole editor schema so a single page '
                    'is enough to confirm rendering in the viewer.'
                )),
                tiptap.full_schema_showcase(),
            ],
        ), title=scenario_name('News', 'Feature Showcase (Every Node And Mark)')),

        _make_article(admin, tiptap.news_article_content(
            headline='Registration is open',
            standfirst='Every team that met the member requirement has been accepted.',
            sections=[
                ('What changed', 'The minimum team size dropped to two so smaller teams can compete.'),
                ('What to do', 'Confirm your roster in the team settings before the first round starts.'),
            ],
        ), title=scenario_name('News', 'Registration Open (Short Update)')),

        _make_article(admin, tiptap.news_article_content(
            headline='A very long announcement',
            standfirst='Intentionally long, so the news card truncates it and shows the expand control.',
            sections=[
                (
                    f'Section {section}',
                    ' '.join([
                        'Filler sentence explaining the change in enough detail '
                        'to make the news card collapse and reveal the expand control.'
                    ] * 12),
                )
                for section in range(1, 7)
            ],
        ), title=scenario_name('News', 'Long Article (Tests Collapsing)')),
    ]


def seed_notifications(users: dict) -> dict:
    """Notifications built from the real event registry.

    Only keys present in ``notifications.config.EVENTS`` are used, and titles
    and messages come from that registry's own templates, so a seeded row is
    indistinguishable from one the app created.

    ``team_member_left`` and ``team_member_removed`` stand in for the two
    membership-history scenarios: ``TeamMember`` has no status column, so the
    only surviving evidence that somebody left or was removed is the
    notification the app emitted at the time.
    """
    recipients = [
        users['admin'], users['organizer'], users['captain'], users['onboarder'], *users['jury'],
    ]
    examples = [
        ('news_published', {'news_id': 1, 'news_title': scenario_name('News', 'Welcome Guide (Structured Content)')}),
        ('team_invitation_received', {'team_id': 11, 'team_name': scenario_name('Team', 'Full Active Roster'), 'user_id': 12, 'invited_by': 'Seed Captain'}),
        ('team_invitation_accepted', {'user_id': 12, 'user_name': 'Seed Accepted Invitee', 'team_id': 13, 'team_name': scenario_name('Team', 'Accepted Invitation')}),
        ('team_invitation_declined', {'user_id': 14, 'user_name': 'Seed Declined Invitee', 'team_id': 15, 'team_name': scenario_name('Team', 'Declined Invitation')}),
        ('team_join_request_received', {'user_id': 16, 'user_name': 'Seed Applicant', 'team_id': 17, 'team_name': scenario_name('Team', 'Pending Join Requests')}),
        ('team_join_request_accepted', {'team_id': 18, 'team_name': scenario_name('Team', 'Accepted Join Request')}),
        ('team_join_request_declined', {'team_id': 19, 'team_name': scenario_name('Team', 'Declined Join Request')}),
        ('team_member_left', {'user_id': 20, 'user_name': 'Seed Former Member (Left Voluntarily)', 'team_id': 21, 'team_name': scenario_name('Team', 'Full Active Roster')}),
        ('team_member_removed', {'user_id': 22, 'user_name': 'Seed Banned Member (Removed By Captain)', 'team_id': 21, 'team_name': scenario_name('Team', 'Full Active Roster')}),
        ('tournament_team_registered', {'team_name': scenario_name('Team', 'Alpha (Open Registration)'), 'tournament_name': scenario_name('Tournament', 'Mixed Registration States')}),
        ('tournament_team_unregistered', {'team_name': scenario_name('Team', 'Forge (Cancelled Registration)'), 'tournament_name': scenario_name('Tournament', 'Running With Cancelled Registration')}),
        ('tournament_team_disqualified', {
            'team_name': scenario_name('Team', 'Outrider (Running Tournament)'),
            'tournament_name': scenario_name('Tournament', 'Running With Disqualified Team'),
            'reason': 'Disqualified: the repository contains a solution copied from another team.',
        }),
        ('tournament_round_started', {'round_name': scenario_name('Round', 'Submissions Open (Active)'), 'tournament_name': scenario_name('Tournament', 'Running With Disqualified Team')}),
        ('tournament_round_submissions_closed', {'round_name': scenario_name('Round', 'Evaluated (Rank Elimination)'), 'tournament_name': scenario_name('Tournament', 'Finished With Final Standings')}),
        ('tournament_round_evaluated', {'round_name': scenario_name('Round', 'Evaluated (Final Standings)'), 'tournament_name': scenario_name('Tournament', 'Finished With Final Standings')}),
        ('tournament_finished', {'tournament_name': scenario_name('Tournament', 'Finished With Final Standings')}),
        ('jury_assignment_received', {'round_name': scenario_name('Round', 'Submissions Open (Active)'), 'tournament_name': scenario_name('Tournament', 'Running With Disqualified Team')}),
    ]

    made = {'notifications': 0, 'delivery_tasks': 0}
    for index, (event_key, context) in enumerate(examples):
        event = NOTIFICATION_EVENTS.get(event_key)
        if event is None:
            # Never invent an event type the app does not support.
            continue
        title, message, _ = event.format(context)
        for recipient in recipients[: (index % len(recipients)) + 1]:
            _, created = Notification.objects.get_or_create(
                recipient=recipient, event_type=event_key, title=title,
                defaults={'message': message, 'is_read': index % 3 == 0},
            )
            made['notifications'] += 1 if created else 0

        recipient = recipients[index % len(recipients)]
        status = ('pending', 'processing', 'sent', 'failed')[index % 4]
        _, created = NotificationDeliveryTask.objects.get_or_create(
            recipient=recipient, event_type=event_key, title=title,
            defaults={
                'channel': 'email',
                'message': message,
                'status': status,
                'attempts': 0 if status == 'pending' else 1,
                'last_error': 'SMTP connection refused.' if status == 'failed' else '',
            },
        )
        made['delivery_tasks'] += 1 if created else 0

    return made


def seed_calendar(tournaments: OrderedDict) -> int:
    """Calendar events spanning past, present, and future."""
    meet_icon = get_or_create_icon('meet_default', 'icons/camera.svg')
    event_icon = get_or_create_icon('event_default', 'icons/calendar.svg')
    plans = [
        ('Tournament — Running With Disqualified Team', 'meet', 'Kickoff Meeting', -days(10), meet_icon),
        ('Tournament — Running With Disqualified Team', 'event', 'Submissions Open', -days(2), event_icon),
        ('Tournament — Running With Disqualified Team', 'meet', 'Jury Calibration Call', +days(2), meet_icon),
        ('Tournament — Running With Disqualified Team', 'event', 'Submissions Deadline', +days(5), event_icon),
        ('Tournament — Running With Cancelled Registration', 'event', 'Round Started', -days(1), event_icon),
        ('Tournament — Finished With Final Standings', 'event', 'Awards Ceremony', -days(5), event_icon),
        ('Tournament — Mixed Registration States', 'meet', 'Registration Closes Soon', +days(1), meet_icon),
    ]
    count = 0
    for tournament_name, event_type, title, offset, icon in plans:
        tournament = tournaments.get(tournament_name)
        if tournament is None:
            continue
        start = (now() + offset).replace(hour=10, minute=0, second=0, microsecond=0)
        _, created = Event.objects.get_or_create(
            tournament=tournament,
            title=scenario_name('Event', title),
            defaults={
                'type': event_type,
                'description': f'{title} for {tournament.name}.',
                'link': 'https://meet.seed.invalid/seed-room',
                'start_datetime': start,
                'icon': icon,
            },
        )
        count += 1 if created else 0
    return count
