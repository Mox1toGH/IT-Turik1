# devtools

Development-only helpers. This app has **no models and no migrations**; it
exists so the management command below can be discovered by Django.

## `seed_dev`

Populates a development database with coherent, scenario-named data so that
every business state can be inspected in the running application.

```bash
cd backend
python manage.py seed_dev                    # medium (default)
python manage.py seed_dev --size small
python manage.py seed_dev --size large
python manage.py seed_dev --reset            # delete seeded rows, then rebuild
python manage.py seed_dev --seed 42          # deterministic random seed
python manage.py seed_dev --only news,calendar
python manage.py seed_dev --force            # with ALLOW_SEED=1
```

### Safety

The command refuses to run unless it is plainly a development environment. It
requires `DEBUG=True`; if `DEBUG` is off it additionally demands both
`ALLOW_SEED=1` in the environment and `--force`. Seeding is rejected outright
when the database is not local SQLite, or when the database name contains
`prod`, `live`, or `staging`.

Outbound email is redirected to Django's in-memory backend for the duration of
the run, and the Google Calendar `post_save` receivers are disconnected so that
creating Events and Rounds does not attempt outbound API calls.

### Accounts

Every generated account uses the `@seed.local` email domain and the shared
password `Test1234$`. The command prints a table of logins at the end.

| Email | Role | Notes |
|---|---|---|
| `admin@seed.local` | admin | superuser |
| `organizer@seed.local` | organizer | creates tournaments |
| `jury.01@seed.local` … `jury.04@seed.local` | jury | score submissions |
| `captain@seed.local` | team | plain team member |
| `onboarding@seed.local` | team | `needs_onboarding=True` |

Password hashes for seeded accounts use a cheap PBKDF2 variant
(`devtools.seeders.base.SeedPasswordHasher`). Django's default hasher costs
roughly 0.6 s per password, which would add minutes to a seed run, and these
accounts all share a password that the command prints in plain text. The
configured hashers are restored immediately after seeding. **Never use this
hasher for real accounts.**

### Sizes

The same set of scenarios is created at every size; only bulk volume changes.
Bulk entities deliberately carry no invitations, requests, or registrations, so
they never violate the rule that a team and its members may take part in only
one `registration`/`running` tournament at a time.

| Area | `small` | `medium` (default) | `large` |
|---|---|---|---|
| Bulk users | 8 | 30 | 120 |
| Bulk teams | 2 | 10 | 45 |
| Bulk tournaments | 0 | 4 | 15 |
| Scenario entities | identical | identical | identical |
| Approx. runtime | ~4 s | ~5 s | ~7 s |

Bulk entities are named with a `seed_` prefix and a descriptive label, for
example `seed_Team Bulk 001` and `seed_Tournament Bulk 001`.

### Scenarios

Entities are named after the state they demonstrate, so a developer can find a
scenario by reading names.

**Teams**

- `Team — Captain Only (No Members Yet)`
- `Team — Full Active Roster`
- `Team — Pending Invitation`
- `Team — Accepted Invitation`
- `Team — Declined Invitation`
- `Team — Pending Join Requests`
- `Team — Accepted Join Request`
- `Team — Declined Join Request`
- `Team — Private (Hidden From List)`

**Tournaments and registration**

- `Tournament — No Registrations Yet`
- `Tournament — Mixed Registration States` (active, withdrawn, disqualified)
- `Tournament — Full At Max Teams` (registered count equals `max_teams`)
- `Tournament — Running With Disqualified Team`
- `Tournament — Running With Cancelled Registration`
- `Tournament — Finished With Final Standings`
- `Tournament — Draft Without Rounds`

**Rounds**

- `Round — Submissions Open (Active)` — submissions in progress, jury assigned, nothing scored
- `Round — In Evaluation (Submission Closed)` — deadline passed, jury still scoring
- `Round — Not Started (Draft)` — scheduled for the future
- `Round — Evaluated (Rank Elimination)` — `passing_count` applied
- `Round — Evaluated (Final Standings)` — tournament leaderboard written

**News** — a structured guide, a full-schema showcase, a short update, and a
deliberately long article that triggers the card's expand control.

### How invariants are enforced

Records are created through the real services and validators wherever possible,
so an invalid state cannot be written:

- `start_round`, `apply_passing_count`, and `save_leaderboard_snapshot` drive the
  round lifecycle, rank elimination, and standings, so those results are
  computed rather than invented.
- Every write passes `full_clean()`, so `Round.clean()`, `Submission.clean()`,
  and `NewsArticle.clean()` all apply.
- `TeamInvitation` and `TeamJoinRequest` are unique on `(team, user)`; the
  seeder re-points an existing row exactly as `teams/api.py` does, rather than
  inserting a duplicate.
- An accepted invitation is always accompanied by a `TeamMember` row, and a
  declined one never is, mirroring the API.

Two states cannot be produced by replaying the live services and are therefore
written directly, with a comment saying so:

1. **Historical rounds.** `start_round` refuses a round whose deadline has
   already passed, so the finished tournament's rounds are stepped through the
   same `draft → active → submission_closed → evaluated` machine by writing the
   status. All *derived* results still come from production code.
2. **Round in evaluation.** Same reason: a round under jury review has passed
   its deadline.

### Membership history

`TeamMember` is a bare through model with no status column, so "left
voluntarily", "removed by the captain", and "banned" cannot be represented as
membership rows. Both membership-removal paths `DELETE` the row, and the only
surviving evidence is the notification the app emitted. The seeder therefore
creates `team_member_left` and `team_member_removed` notifications, which is the
truthful representation of that history. (Note that the app has no ban feature:
being "banned" is modelled as removal.)

### Reruns

The command is safe to rerun. Every record is created with `get_or_create`
against the seeder naming convention, so a second run refreshes existing rows
instead of duplicating them, and `--reset` can always find the seeded rows again
to delete them. Rerunning at a different `--size` neither adds nor removes
records; it only creates the extra bulk entities.

### `--only`

Only the standalone areas (`news`, `notifications`, `calendar`) can be limited.
The remaining areas (`users`, `teams`, `tournaments`, `rounds`, `submissions`,
`evaluations`) are built as one coherent chain and are always created, because
individual scenarios are meaningless without the records they depend on.
