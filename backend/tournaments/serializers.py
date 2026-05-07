from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import serializers

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
    register_team_for_tournament,
)
from teams.serializers import TeamSummarySerializer


class RoundShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Round
        fields = ('id', 'name', 'start_date', 'end_date', 'status')


class TournamentPublicSerializer(serializers.ModelSerializer):
    rounds = RoundShortSerializer(many=True, read_only=True)

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
            'status',
            'rounds',
        )


class ActiveTournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = ('id', 'name', 'status', 'start_date')


class TournamentAdminSerializer(TournamentPublicSerializer):
    class Meta(TournamentPublicSerializer.Meta):
        read_only_fields = ('status',)

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
        start_date = attrs.get('start_date', getattr(instance, 'start_date', None))
        end_date = attrs.get('end_date', getattr(instance, 'end_date', None))
        errors = {}

        if start_date and end_date and start_date >= end_date:
            errors['end_date'] = 'end_date must be greater than start_date.'

        if tournament and start_date and end_date:
            if start_date < tournament.start_date or end_date > tournament.end_date:
                errors['start_date'] = 'Round dates must be within tournament dates.'

        passing_count = attrs.get('passing_count', getattr(instance, 'passing_count', None))
        if passing_count is not None and tournament:
            registered_teams_count = tournament.team_registrations.count()
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


class SubmissionSerializer(serializers.ModelSerializer):
    team_details = TeamSummarySerializer(source='team', read_only=True)
    round_details = RoundShortSerializer(source='round', read_only=True)

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
            'created_at',
            'updated_at',
        )
        read_only_fields = ('created_at', 'updated_at')
        extra_kwargs = {
            'team': {'write_only': True},
            'round': {'write_only': True},
        }

    def _request_user(self):
        request = self.context.get('request')
        if not request:
            return None
        return request.user

    def validate(self, attrs):
        instance = self.instance
        user = self._request_user()
        team = attrs.get('team', getattr(instance, 'team', None))
        round_obj = attrs.get('round', getattr(instance, 'round', None))
        github_url = attrs.get('github_url', getattr(instance, 'github_url', ''))
        demo_video_url = attrs.get('demo_video_url', getattr(instance, 'demo_video_url', ''))
        demo_video_file = attrs.get('demo_video_file', getattr(instance, 'demo_video_file', None))

        errors = {}

        if not github_url:
            errors['github_url'] = 'github_url is required.'

        if not demo_video_url and not demo_video_file:
            errors['demo_video_url'] = 'Provide demo_video_url or demo_video_file.'

        if not team:
            errors['team'] = 'team is required.'

        if not round_obj:
            errors['round'] = 'round is required.'

        if instance is not None:
            if 'team' in attrs and attrs['team'].id != instance.team_id:
                errors['team'] = 'team cannot be changed.'
            if 'round' in attrs and attrs['round'].id != instance.round_id:
                errors['round'] = 'round cannot be changed.'

        if team and user and not TeamMember.objects.filter(team=team, user=user).exists() and team.captain_id != user.id:
            errors['team'] = 'You are not a member of this team.'

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
        fields = ('id', 'tournament', 'team', 'team_name', 'is_active', 'created_at')
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


class TournamentTeamRegistrationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TournamentTeamRegistration
        fields = ('is_active',)


class TournamentTeamRegistrationListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='team.id')
    name = serializers.CharField(source='team.name')
    is_public = serializers.BooleanField(source='team.is_public')
    members_count = serializers.SerializerMethodField()
 
    class Meta:
        model = TournamentTeamRegistration
        fields = ('id', 'name', 'members_count', 'is_public', 'is_active')
 
    def get_members_count(self, obj):
        return obj.team.team_members.count() + 1  # members + captain


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
            'end_datetime',
            'icon',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('created_at', 'updated_at')

    def validate(self, attrs):
        instance = self.instance
        event_type = attrs.get('type', getattr(instance, 'type', None))
        start_datetime = attrs.get('start_datetime', getattr(instance, 'start_datetime', None))
        end_datetime = attrs.get('end_datetime', getattr(instance, 'end_datetime', None))
        errors = {}

        if end_datetime and start_datetime and end_datetime < start_datetime:
            errors['end_datetime'] = 'end_datetime must be greater than or equal to start_datetime.'

        if event_type == Event.TYPE_EVENT:
            attrs.pop('link', None)
            attrs['link'] = ''

        if errors:
            raise serializers.ValidationError(errors)

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