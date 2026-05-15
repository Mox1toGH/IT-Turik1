from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone
from typing import Any
from rest_framework import serializers

from evaluation.models import JuryAssignment
from evaluation.models import SubmissionEvaluation
from teams.models import Team
from teams.models import TeamMember

from .models import (
    Event,
    Icon,
    Round,
    Submission,
    Tournament,
    TournamentTeamRegistration,
)
from .services import (
    ensure_team_registered_for_tournament,
    leave_team_from_tournament,
    register_team_for_tournament,
)
from teams.serializers import TeamMemberSerializer, TeamSummarySerializer
from evaluation.models import LeaderboardEntry

from drf_spectacular.utils import extend_schema_field


class CriterionSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
    max_score = serializers.FloatField()

class RoundShortSerializer(serializers.ModelSerializer):
    criteria = CriterionSerializer(many=True)

    class Meta:
        model = Round
        fields = (
            'id',
            'name',
            'start_date',
            'end_date',
            'status',
            'criteria',
            'tournament',
        )


class TournamentPublicSerializer(serializers.ModelSerializer):
    rounds = RoundShortSerializer(many=True, read_only=True)
    registered_team = serializers.SerializerMethodField()


    class Meta:
        model = Tournament
        fields = (
            'id',
            'name',
            'description',
            'start_date',
            'end_date',
            'max_teams',
            'min_team_members',
            'banner',
            'status',
            'rounds',
            'registered_team',
        )

    @extend_schema_field(TeamSummarySerializer)
    def get_registered_team(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None

        user = request.user
        user_team_ids = set(
            TeamMember.objects.filter(user=user).values_list('team_id', flat=True)
        ) | set(
            Team.objects.filter(captain=user).values_list('id', flat=True)
        )

        registration = (
            obj.team_registrations
            .filter(team_id__in=user_team_ids, is_active=True)
            .select_related('team')
            .first()
        )

        if not registration:
            return None

        return TeamSummarySerializer(registration.team, context=self.context).data


class ActiveTournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = ('id', 'name', 'status', 'start_date')

class TournamentBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = ('banner',)

class TournamentAdminSerializer(TournamentPublicSerializer):
    class Meta(TournamentPublicSerializer.Meta):
        read_only_fields = ('status', 'banner')

    def validate(self, attrs):
        start_date = attrs.get('start_date', getattr(self.instance, 'start_date', None))
        end_date = attrs.get('end_date', getattr(self.instance, 'end_date', None))
        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError({'end_date': 'end_date must be greater than start_date.'})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get('request')
        tournament = Tournament(created_by=getattr(request, 'user', None), **validated_data)
        try:
            tournament.full_clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict) from None
        tournament.save()
        return tournament

    @transaction.atomic
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        try:
            instance.full_clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict) from None
        instance.save()
        return instance


class RoundSerializer(serializers.ModelSerializer):
    criteria = CriterionSerializer(many=True)

    class Meta:
        model = Round
        fields = (
            'id',
            'tournament',
            'name',
            'description',
            'tech_requirements',
            'must_have_requirements',
            'criteria',
            'start_date',
            'end_date',
            'passing_count',
            'evaluation_criteria',
            'materials',
            'status',
        )
        read_only_fields = ('status',)
        extra_kwargs = {
            'tournament': {'required': False},
        }

    def validate(self, attrs):
        instance = self.instance
        tournament = attrs.get('tournament', getattr(instance, 'tournament', None))
        errors = {}

        passing_count = attrs.get('passing_count', getattr(instance, 'passing_count', None))
        if passing_count is not None and tournament:
            registered_teams_count = tournament.team_registrations.filter(is_active=True).count()
            if registered_teams_count > 0 and passing_count > registered_teams_count:
                errors['passing_count'] = (
                    f'passing_count ({passing_count}) cannot exceed '
                    f'the number of registered teams ({registered_teams_count}).'
                )

        for field in ['tech_requirements', 'must_have_requirements', 'description']:
            val = attrs.get(field)
            if val is not None and not isinstance(val, dict):
                errors[field] = f'{field} must be a JSON object (dict).'

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        round_obj = Round(**validated_data)
        try:
            round_obj.full_clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict) from None
        round_obj.save()
        return round_obj

    @transaction.atomic
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        try:
            instance.full_clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict) from None
        instance.save()
        return instance


class SubmissionAssignmentJurySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    full_name = serializers.CharField()
    role = serializers.CharField()


class ScoreItemSerializer(serializers.Serializer):
    criterion_id = serializers.CharField()
    criterion_name = serializers.CharField()
    score = serializers.IntegerField()


class SubmissionEvaluationSerializer(serializers.ModelSerializer):
    scores = ScoreItemSerializer(many=True, read_only=True)
    final_score = serializers.FloatField(read_only=True)

    class Meta:
        model = SubmissionEvaluation
        fields = (
            'id',
            'scores',
            'total_score',
            'final_score',
            'comment',
            'created_at',
        )


class SubmissionAssignmentSerializer(serializers.ModelSerializer):
    jury = SubmissionAssignmentJurySerializer(read_only=True)
    evaluation = SubmissionEvaluationSerializer(read_only=True)

    class Meta:
        model = JuryAssignment
        fields = ('id', 'jury', 'evaluation', 'created_at')

    def get_evaluation(self, obj):
        evaluation = getattr(obj, 'evaluation', None)
        if evaluation is None:
            return None
        return {
            'id': evaluation.id,
            'scores': evaluation.scores,
            'total_score': evaluation.total_score,
            'final_score': evaluation.final_score,
            'comment': evaluation.comment,
            'created_at': evaluation.created_at,
        }


class SubmissionSerializer(serializers.ModelSerializer):
    team_details = TeamSummarySerializer(source='team', read_only=True)
    round_details = RoundShortSerializer(source='round', read_only=True)
    assignments = SubmissionAssignmentSerializer(source='jury_assignments', many=True, read_only=True)

    class Meta:
        model = Submission
        fields = (
            'id',
            'team',
            'round',
            'team_details',
            'round_details',
            'github_url',
            'demo_video_url',
            'demo_video_file',
            'live_demo_url',
            'description',
            'assignments',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('created_at', 'updated_at')
        extra_kwargs = {
            'team': {'read_only': True},
            'round': {'write_only': True},
        }

    def _request_user(self):
        request = self.context.get('request')
        if not request:
            return None
        return request.user

    def _resolve_captain_team_for_round(self, *, user, round_obj):
        if not user or not round_obj:
            return None

        registrations = (
            TournamentTeamRegistration.objects.select_related('team')
            .filter(
                tournament=round_obj.tournament,
                is_active=True,
                team__captain_id=user.id,
            )
            .order_by('id')
        )
        registration_count = registrations.count()
        if registration_count == 0:
            raise serializers.ValidationError(
                {'team': 'Only team captain can create submissions for an active registered team in this tournament.'}
            )
        if registration_count > 1:
            raise serializers.ValidationError(
                {'team': 'Multiple active captain teams found in this tournament. Please contact support.'}
            )
        return registrations.first().team

    def validate(self, attrs):
        instance = self.instance
        user = self._request_user()
        round_obj = attrs.get('round', getattr(instance, 'round', None))
        github_url = attrs.get('github_url', getattr(instance, 'github_url', ''))
        demo_video_url = attrs.get('demo_video_url', getattr(instance, 'demo_video_url', ''))
        demo_video_file = attrs.get('demo_video_file', getattr(instance, 'demo_video_file', None))

        errors = {}

        if not github_url:
            errors['github_url'] = 'github_url is required.'

        if not demo_video_url and not demo_video_file:
            errors['demo_video_url'] = 'Provide demo_video_url or demo_video_file.'

        if not round_obj:
            errors['round'] = 'round is required.'

        if instance is not None:
            if 'team' in attrs and attrs['team'].id != instance.team_id:
                errors['team'] = 'team cannot be changed.'
            if 'round' in attrs and attrs['round'].id != instance.round_id:
                errors['round'] = 'round cannot be changed.'

        team = getattr(instance, 'team', None)
        if instance is None and not errors:
            team = self._resolve_captain_team_for_round(user=user, round_obj=round_obj)
            attrs['team'] = team
        elif team and user and team.captain_id != user.id:
            errors['team'] = 'Only team captain can create or update submissions.'

        if round_obj:
            now = timezone.now()
            if round_obj.status != Round.STATUS_ACTIVE or round_obj.end_date <= now:
                errors['round'] = 'Round is closed for submissions.'

        if not errors and instance is None and team and round_obj:
            ensure_team_registered_for_tournament(
                tournament=round_obj.tournament,
                team=team,
            )

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get('request')
        try:
            return Submission.objects.create(created_by=getattr(request, 'user', None), **validated_data)
        except IntegrityError:
            raise serializers.ValidationError({'team': 'Only one submission per team per round is allowed.'}) from None


class OwnSubmissionSerializer(serializers.ModelSerializer):
    team = TeamSummarySerializer(read_only=True)
    round = RoundShortSerializer(read_only=True)

    class Meta:
        model = Submission
        fields = (
            'id',
            'team',
            'round',
            'github_url',
            'demo_video_url',
            'demo_video_file',
            'live_demo_url',
            'description',
            'created_at',
            'updated_at',
        )


class CurrentTaskSerializer(serializers.ModelSerializer):
    tournament_id = serializers.IntegerField(source='tournament.id', read_only=True)
    tournament_name = serializers.CharField(source='tournament.name', read_only=True)
    deadline = serializers.DateTimeField(source='end_date', read_only=True)
    task = serializers.CharField(source='description', read_only=True)

    class Meta:
        model = Round
        fields = (
            'id',
            'tournament_id',
            'tournament_name',
            'name',
            'task',
            'deadline',
            'must_have_requirements',
            'tech_requirements',
        )


class TournamentTeamRegistrationSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source='team.name', read_only=True)

    class Meta:
        model = TournamentTeamRegistration
        fields = (
            'id',
            'tournament',
            'team',
            'team_name',
            'is_active',
            'is_disqualified',
            'disqualification_reason',
            'created_at',
        )
        read_only_fields = ('id', 'tournament', 'created_at')


class TournamentTeamRegistrationCreateSerializer(serializers.Serializer):
    team_id = serializers.PrimaryKeyRelatedField(queryset=Team.objects.all(), source='team')

    def save(self, **kwargs):
        request = self.context['request']
        tournament = self.context['tournament']
        team = self.validated_data['team']
        return register_team_for_tournament(
            tournament=tournament,
            team=team,
            actor=request.user,
        )


class TournamentTeamLeaveSerializer(serializers.Serializer):
    team_id = serializers.PrimaryKeyRelatedField(queryset=Team.objects.all(), source='team')

    def save(self, **kwargs):
        request = self.context['request']
        tournament = self.context['tournament']
        team = self.validated_data['team']
        return leave_team_from_tournament(
            tournament=tournament,
            team=team,
            actor=request.user,
        )


class TournamentTeamRegistrationDisqualificationSerializer(serializers.Serializer):
    ACTION_DISQUALIFY = 'disqualify'
    ACTION_REACTIVATE = 'reactivate'
    ACTION_CHOICES = (ACTION_DISQUALIFY, ACTION_REACTIVATE)

    action = serializers.ChoiceField(choices=ACTION_CHOICES)
    disqualification_reason = serializers.CharField(required=False, allow_blank=True)

    def update(self, instance, validated_data):
        action = validated_data['action']
        if action == self.ACTION_DISQUALIFY:
            instance.is_active = False
            instance.is_disqualified = True
            reason = validated_data.get('disqualification_reason', '').strip()
            instance.disqualification_reason = reason or 'Disqualified by admin'
        else:
            instance.is_active = True
            instance.is_disqualified = False
            instance.disqualification_reason = ''

        instance.save(update_fields=['is_active', 'is_disqualified', 'disqualification_reason'])
        return instance

class TournamentTeamRegistrationListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='team.id')
    registration_id = serializers.IntegerField(source='pk')
    name = serializers.CharField(source='team.name')
    is_public = serializers.BooleanField(source='team.is_public')
    members_count = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()
    is_disqualified = serializers.BooleanField()
 
    class Meta:
        model = TournamentTeamRegistration
        fields = (
            'id',
            'registration_id',
            'name',
            'members_count',
            'members',
            'is_public',
            'is_active',
            'is_disqualified',
            'disqualification_reason',
        )
 
    def get_members_count(self, obj) -> int:
        return len(self._get_unique_team_users(obj))

    def _get_unique_team_users(self, obj):
        users = list(obj.team.members.all())
        if obj.team.captain_id is not None:
            users.append(obj.team.captain)

        seen = set()
        unique_users = []
        for user in users:
            if user is None or user.id in seen:
                continue
            seen.add(user.id)
            unique_users.append(user)
        return unique_users

    def get_members(self, obj) -> list[dict[str, Any]]:
        return TeamMemberSerializer(self._get_unique_team_users(obj), many=True).data


class IconSerializer(serializers.ModelSerializer):
    class Meta:
        model = Icon
        fields = ('id', 'name', 'path')


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = (
            'id',
            'tournament',
            'type',
            'title',
            'description',
            'link',
            'start_datetime',
            'icon',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('created_at', 'updated_at')

    def validate(self, attrs):
        instance = self.instance
        event_type = attrs.get('type', getattr(instance, 'type', None))

        if event_type == Event.TYPE_EVENT:
            attrs.pop('link', None)
            attrs['link'] = ''

        return attrs

    def _resolve_default_icon(self, event_type):
        if event_type == Event.TYPE_MEET:
            default_name = 'meet_default'
        else:
            default_name = 'event_default'
        return Icon.objects.filter(name=default_name).first()

    @transaction.atomic
    def create(self, validated_data):
        if 'icon' not in validated_data or validated_data['icon'] is None:
            validated_data['icon'] = self._resolve_default_icon(validated_data.get('type'))
        return Event.objects.create(**validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        if 'icon' in validated_data and validated_data['icon'] is None:
            validated_data['icon'] = self._resolve_default_icon(
                validated_data.get('type', instance.type)
            )
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ArchiveStandingSerializer(serializers.ModelSerializer):
    team = TeamSummarySerializer(read_only=True)

    class Meta:
        model = LeaderboardEntry
        fields = (
            'rank',
            'team',
            'total_score',
            'average_score',
            'criteria_breakdown',
            'jury_breakdown',
            'rounds_breakdown',
            'snapshot_at',
        )


class TournamentArchiveListSerializer(serializers.ModelSerializer):
    teams = serializers.SerializerMethodField()
    standings = serializers.SerializerMethodField()

    class Meta:
        model = Tournament
        fields = (
            'id',
            'name',
            'description',
            'start_date',
            'end_date',
            'status',
            'banner',
            'teams',
            'standings',
        )

    def get_teams(self, obj):
        registrations = (
            obj.team_registrations
            .select_related('team')
            .filter(is_active=True)
            .order_by('team__name')
        )
        return TeamSummarySerializer([r.team for r in registrations], many=True, context=self.context).data

    def get_standings(self, obj):
        standings = (
            obj.leaderboard_entries
            .filter(round__isnull=True)
            .select_related('team')
            .order_by('rank')
        )
        return ArchiveStandingSerializer(standings, many=True, context=self.context).data


class TournamentArchiveDetailSerializer(serializers.ModelSerializer):
    rounds = RoundShortSerializer(many=True, read_only=True)
    teams = serializers.SerializerMethodField()
    standings = serializers.SerializerMethodField()

    class Meta:
        model = Tournament
        fields = (
            'id',
            'name',
            'description',
            'start_date',
            'end_date',
            'status',
            'banner',
            'rounds',
            'teams',
            'standings',
        )

    def get_teams(self, obj):
        registrations = (
            obj.team_registrations
            .select_related('team')
            .filter(is_active=True)
            .order_by('team__name')
        )
        return TeamSummarySerializer([r.team for r in registrations], many=True, context=self.context).data

    def get_standings(self, obj):
        standings = (
            obj.leaderboard_entries
            .filter(round__isnull=True)
            .select_related('team')
            .order_by('rank')
        )
        return ArchiveStandingSerializer(standings, many=True, context=self.context).data

class TournamentArchiveListSerializer(serializers.ModelSerializer):
    teams = serializers.SerializerMethodField()
    standings = serializers.SerializerMethodField()

    class Meta:
        model = Tournament
        fields = (
            'id',
            'name',
            'description',
            'start_date',
            'end_date',
            'status',
            'banner',
            'teams',
            'standings',
        )

    @extend_schema_field(TeamSummarySerializer(many=True))
    def get_teams(self, obj):
        registrations = (
            obj.team_registrations
            .select_related('team')
            .filter(is_active=True)
            .order_by('team__name')
        )
        return TeamSummarySerializer([r.team for r in registrations], many=True, context=self.context).data

    @extend_schema_field(ArchiveStandingSerializer(many=True))
    def get_standings(self, obj):
        standings = (
            obj.leaderboard_entries
            .filter(round__isnull=True)
            .select_related('team')
            .order_by('rank')
        )
        return ArchiveStandingSerializer(standings, many=True, context=self.context).data


class TournamentArchiveDetailSerializer(serializers.ModelSerializer):
    rounds = RoundShortSerializer(many=True, read_only=True)
    teams = serializers.SerializerMethodField()
    standings = serializers.SerializerMethodField()

    class Meta:
        model = Tournament
        fields = (
            'id',
            'name',
            'description',
            'start_date',
            'end_date',
            'status',
            'banner',
            'rounds',
            'teams',
            'standings',
        )

    @extend_schema_field(TeamSummarySerializer(many=True))
    def get_teams(self, obj):
        registrations = (
            obj.team_registrations
            .select_related('team')
            .filter(is_active=True)
            .order_by('team__name')
        )
        return TeamSummarySerializer([r.team for r in registrations], many=True, context=self.context).data

    @extend_schema_field(ArchiveStandingSerializer(many=True))
    def get_standings(self, obj):
        standings = (
            obj.leaderboard_entries
            .filter(round__isnull=True)
            .select_related('team')
            .order_by('rank')
        )
        return ArchiveStandingSerializer(standings, many=True, context=self.context).data


class TournamentListResponseSerializer(serializers.Serializer):
    data = TournamentPublicSerializer(many=True)
    total = serializers.IntegerField()


class DisqualificationResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    team_id = serializers.IntegerField()
    team_name = serializers.CharField()
    tournament_id = serializers.IntegerField()
    is_active = serializers.BooleanField()
    action = serializers.CharField()


class EligibleTeamSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    members_count = serializers.IntegerField()
