from ninja import Schema

class PlayerStatsResponse(Schema):
    total_tournaments: int
    wins: int
    losses: int
    win_rate: float
    average_evaluation_score: float
    current_team_name: str | None


class TopPlayerResponse(Schema):
    id: int
    username: str
    average_evaluation_score: float


class TeamStatsResponse(Schema):
    team_id: int
    team_name: str
    total_tournaments: int
    wins: int
    losses: int
    win_rate: float
    average_member_evaluation_score: float
    active_members_count: int
    top_player: TopPlayerResponse | None


class TopTeamResponse(Schema):
    team_id: int
    team_name: str
    rank: int | None = None
    average_score: float


class TournamentStatsResponse(Schema):
    tournament_id: int
    tournament_name: str
    total_registered_teams: int
    total_registered_players: int
    fill_rate: float
    completed_matches: int
    total_matches: int
    average_evaluation_score: float
    top_teams: list[TopTeamResponse]


class RoleBreakdownResponse(Schema):
    role: str
    count: int


class AdminStatsResponse(Schema):
    total_users: int
    total_teams: int
    total_tournaments: int
    new_registrations_last_7_days: int
    new_registrations_last_30_days: int
    active_tournaments: int
    users_by_role: list[RoleBreakdownResponse]
    total_evaluation_records: int
