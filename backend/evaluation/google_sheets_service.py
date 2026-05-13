import json
from datetime import datetime
from typing import Any

import gspread
from django.conf import settings
from google.oauth2.service_account import Credentials
from rest_framework.exceptions import ValidationError

from tournaments.models import Round

GOOGLE_SHEETS_SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
]


def export_tournament_leaderboard_to_google_sheets(
    *,
    tournament_name: str,
    tournament_id: int,
    rankings: list[dict[str, Any]],
    requester_email: str | None = None,
) -> dict[str, str]:
    values = build_tournament_leaderboard_table_rows(tournament_id=tournament_id, rankings=rankings)
    try:
        credentials = _build_google_credentials()
        client = gspread.authorize(credentials)

        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
        sheet_title = f'{tournament_name} Leaderboard ({timestamp})'
        spreadsheet = client.create(sheet_title)
        worksheet = spreadsheet.sheet1
        worksheet.update_title('Leaderboard')
        worksheet.append_rows(values, value_input_option='USER_ENTERED')

        for email in _share_emails(requester_email):
            spreadsheet.share(email, perm_type='user', role='writer', notify=False)
    except ValidationError:
        raise
    except Exception as exc:
        raise ValidationError({'google_sheets': f'Failed to create Google Sheet: {exc}'}) from exc

    return {
        'spreadsheet_id': spreadsheet.id,
        'spreadsheet_url': spreadsheet.url,
        'title': spreadsheet.title,
    }


def build_tournament_leaderboard_table_rows(
    *,
    tournament_id: int,
    rankings: list[dict[str, Any]],
) -> list[list[str]]:
    round_columns, round_max_score_map = _build_round_columns(
        tournament_id=tournament_id,
        rankings=rankings,
    )
    header = ['Place', 'Team', *[column['name'] for column in round_columns], 'Total']
    rows: list[list[str]] = [header]

    for entry in rankings:
        rounds = entry.get('rounds') or []
        rounds_by_id = {round_row['round_id']: round_row for round_row in rounds}

        row = [str(entry.get('rank', '')), str(entry.get('team_name', ''))]

        for round_column in round_columns:
            round_row = rounds_by_id.get(round_column['id'])
            if not round_row:
                row.append('x')
                continue

            round_total_score = _to_float(round_row.get('total_score'))
            round_max_score = round_max_score_map.get(round_column['id'], 0.0)
            jury_count = _get_jury_count(
                jury_breakdown=round_row.get('jury_breakdown'),
                total_score=round_total_score,
                average_score=_to_float(round_row.get('average_score')),
                round_max_score=round_max_score,
            )
            row.append(
                f'{format_score(round_total_score)}/{format_score(round_max_score * jury_count)}',
            )

        total_max_score = 0.0
        for round_row in rounds:
            round_max_score = round_max_score_map.get(round_row.get('round_id'), 0.0)
            jury_count = _get_jury_count(
                jury_breakdown=round_row.get('jury_breakdown'),
                total_score=_to_float(round_row.get('total_score')),
                average_score=_to_float(round_row.get('average_score')),
                round_max_score=round_max_score,
            )
            total_max_score += round_max_score * jury_count

        total_score = _to_float(entry.get('total_score'))
        row.append(f'{format_score(total_score)}/{format_score(total_max_score)}')
        rows.append(row)

    return rows


def _build_google_credentials() -> Credentials:
    raw_info = (getattr(settings, 'GOOGLE_SHEETS_SERVICE_ACCOUNT_INFO', '') or '').strip()
    if not raw_info:
        raise ValidationError(
            {'google_sheets': 'Google Sheets credentials are not configured. Set GOOGLE_SHEETS_SERVICE_ACCOUNT_INFO.'}
        )

    try:
        service_account_info = json.loads(raw_info)
    except json.JSONDecodeError as exc:
        raise ValidationError(
            {'google_sheets': 'GOOGLE_SHEETS_SERVICE_ACCOUNT_INFO must be valid JSON.'}
        ) from exc

    private_key = service_account_info.get('private_key')
    if isinstance(private_key, str):
        service_account_info['private_key'] = private_key.replace('\\n', '\n')

    try:
        return Credentials.from_service_account_info(service_account_info, scopes=GOOGLE_SHEETS_SCOPES)
    except Exception as exc:
        raise ValidationError({'google_sheets': f'Invalid Google Sheets credentials: {exc}'}) from exc


def _build_round_columns(*, tournament_id: int, rankings: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[int, float]]:
    rounds = list(
        Round.objects.filter(tournament_id=tournament_id).order_by('start_date', 'id').only('id', 'name', 'criteria')
    )
    round_max_score_map = {
        round_obj.id: _sum_round_criteria_max_score(round_obj.criteria)
        for round_obj in rounds
    }

    leaderboard_round_ids = {
        round_row['round_id']
        for entry in rankings
        for round_row in (entry.get('rounds') or [])
        if round_row.get('round_id') is not None
    }
    should_filter_by_leaderboard = len(leaderboard_round_ids) > 0

    base_rounds = (
        [round_obj for round_obj in rounds if round_obj.id in leaderboard_round_ids]
        if should_filter_by_leaderboard
        else rounds
    )

    columns = [
        {'id': round_obj.id, 'name': round_obj.name}
        for round_obj in base_rounds
    ]

    if not should_filter_by_leaderboard:
        return columns, round_max_score_map

    existing_ids = {column['id'] for column in columns}

    for entry in rankings:
        for round_row in entry.get('rounds') or []:
            round_id = round_row.get('round_id')
            if round_id is None or round_id in existing_ids:
                continue

            columns.append({
                'id': round_id,
                'name': round_row.get('round_name') or f'Round {round_id}',
            })
            existing_ids.add(round_id)

    return columns, round_max_score_map


def _sum_round_criteria_max_score(criteria: Any) -> float:
    if not isinstance(criteria, list):
        return 0.0

    total = 0.0
    for criterion in criteria:
        if isinstance(criterion, dict):
            total += _to_float(criterion.get('max_score'))
    return total


def _get_jury_count(
    *,
    jury_breakdown: Any,
    total_score: float,
    average_score: float,
    round_max_score: float,
) -> int:
    if isinstance(jury_breakdown, list):
        return len(jury_breakdown) or 1

    if isinstance(jury_breakdown, dict):
        count = len(jury_breakdown.keys())
        return count or 1

    if round_max_score > 0 and average_score > 0:
        estimated = total_score / (round_max_score * average_score)
        if estimated > 0:
            return max(1, round(estimated))

    return 1


def _share_emails(requester_email: str | None) -> set[str]:
    share_emails = set()

    default_share_email = (getattr(settings, 'GOOGLE_SHEETS_DEFAULT_SHARE_WITH', '') or '').strip()
    if default_share_email:
        share_emails.add(default_share_email)

    if requester_email and requester_email.strip():
        share_emails.add(requester_email.strip())

    return share_emails


def _to_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def format_score(value: Any) -> str:
    numeric_value = _to_float(value)
    if numeric_value.is_integer():
        return str(int(numeric_value))
    return f'{numeric_value:.2f}'.rstrip('0').rstrip('.')
