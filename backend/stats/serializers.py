from rest_framework import serializers


class PlayerStatsSerializer(serializers.Serializer):
    total_tournaments = serializers.IntegerField()
    wins = serializers.IntegerField()
    losses = serializers.IntegerField()
    win_rate = serializers.FloatField()
    average_evaluation_score = serializers.FloatField()
    current_team_name = serializers.CharField(allow_null=True)


class TopPlayerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    average_evaluation_score = serializers.FloatField()


class TeamStatsSerializer(serializers.Serializer):
    team_id = serializers.IntegerField()
    team_name = serializers.CharField()
    total_tournaments = serializers.IntegerField()
    wins = serializers.IntegerField()
    losses = serializers.IntegerField()
    win_rate = serializers.FloatField()
    average_member_evaluation_score = serializers.FloatField()
    active_members_count = serializers.IntegerField()
    top_player = TopPlayerSerializer(allow_null=True)


class TopTeamSerializer(serializers.Serializer):
    team_id = serializers.IntegerField()
    team_name = serializers.CharField()
    rank = serializers.IntegerField(allow_null=True)
    average_score = serializers.FloatField()


class TournamentStatsSerializer(serializers.Serializer):
    tournament_id = serializers.IntegerField()
    tournament_name = serializers.CharField()
    total_registered_teams = serializers.IntegerField()
    total_registered_players = serializers.IntegerField()
    fill_rate = serializers.FloatField()
    completed_matches = serializers.IntegerField()
    total_matches = serializers.IntegerField()
    average_evaluation_score = serializers.FloatField()
    top_teams = TopTeamSerializer(many=True)


class RoleBreakdownItemSerializer(serializers.Serializer):
    role = serializers.CharField()
    count = serializers.IntegerField()


class AdminStatsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_teams = serializers.IntegerField()
    total_tournaments = serializers.IntegerField()
    new_registrations_last_7_days = serializers.IntegerField()
    new_registrations_last_30_days = serializers.IntegerField()
    active_tournaments = serializers.IntegerField()
    users_by_role = RoleBreakdownItemSerializer(many=True)
    total_evaluation_records = serializers.IntegerField()
