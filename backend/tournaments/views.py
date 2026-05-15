from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, viewsets
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import OpenApiParameter, extend_schema, OpenApiResponse, inline_serializer
from drf_spectacular.types import OpenApiTypes

from backend.openapi import _400, _401, _403, _404
from teams.models import Team
from .models import Event, Icon, Round, Submission, Tournament, TournamentTeamRegistration
from backend.permissions import Permission, has_permission as user_has_permission

from .permissions import (
    CanCreateTournament,
    CanDeleteTournament,
    CanEditTournament,
    CanManageRounds,
    CanManageRoundsOrReadOnly,
    CanManageParticipants,
    CanRegisterTeamForTournament,
    CanSetResults,
    CanViewTournament,
    IsPlatformAdminOrTeamMemberPermission,
)
from .serializers import (
    TournamentArchiveDetailSerializer,
    TournamentArchiveListSerializer,
    ActiveTournamentSerializer,
    CurrentTaskSerializer,
    DisqualificationResponseSerializer,
    EligibleTeamSerializer,
    EventSerializer,
    IconSerializer,
    OwnSubmissionSerializer,
    RoundSerializer,
    SubmissionSerializer,
    TournamentAdminSerializer,
    TournamentListResponseSerializer,
    TournamentPublicSerializer,
    TournamentTeamRegistrationCreateSerializer,
    TournamentTeamLeaveSerializer,
    TournamentTeamRegistrationListSerializer,
    TournamentTeamRegistrationSerializer,
    TournamentTeamRegistrationDisqualificationSerializer,
    TournamentBannerSerializer,
)
from .services import (
    close_submissions_on_round,
    delete_round,
    mark_round_evaluated,
    start_registration,
    start_round,
    sync_time_based_statuses,
)


def get_tournament_queryset():
    return Tournament.objects.prefetch_related(
        Prefetch('rounds', queryset=Round.objects.order_by('start_date'))
    ).order_by('-created_at')


def get_round_queryset():
    return Round.objects.select_related('tournament').order_by('tournament_id', 'start_date')


def get_own_submissions_queryset(user):
    return (
        Submission.objects.select_related('team', 'round', 'round__tournament')
        .filter(Q(team__captain_id=user.id) | Q(team__team_members__user_id=user.id))
        .distinct()
        .order_by('-updated_at')
    )


class SyncStatusesMixin:
    def initial(self, request, *args, **kwargs):
        sync_time_based_statuses()
        return super().initial(request, *args, **kwargs)


@extend_schema(
    operation_id='listTournaments',
    parameters=[
        OpenApiParameter('page', OpenApiTypes.INT, default=1),
        OpenApiParameter('page_size', OpenApiTypes.INT, default=20),
        OpenApiParameter('searchQuery', OpenApiTypes.STR, required=False),
        OpenApiParameter('status', OpenApiTypes.STR, required=False, description='Comma-separated statuses'),
        OpenApiParameter('startAt', OpenApiTypes.DATE, required=False),
        OpenApiParameter('endAt', OpenApiTypes.DATE, required=False),
        OpenApiParameter('createdAt', OpenApiTypes.DATE, required=False),
    ],
    responses={
        200: TournamentListResponseSerializer,
        400: _400,
    },
)
class TournamentListView(SyncStatusesMixin, generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = TournamentPublicSerializer
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

    def _parse_positive_int(self, value, field_name):
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            raise ValidationError({field_name: 'Must be a positive integer.'})
        if parsed < 1:
            raise ValidationError({field_name: 'Must be a positive integer.'})
        return parsed

    def _get_base_queryset(self):
        user = self.request.user
        base_queryset = get_tournament_queryset()
        published_filter = ~Q(status=Tournament.STATUS_DRAFT)

        if user_has_permission(user, Permission.VIEW_TOURNAMENT):
            return base_queryset

        if user.is_authenticated:
            return base_queryset.filter(published_filter | Q(created_by=user))

        return base_queryset.filter(published_filter)

    def _apply_filters(self, queryset):
        params = self.request.query_params

        search_query = params.get('searchQuery')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query)
            )

        status_param = params.get('status')
        if status_param:
            statuses = [s.strip() for s in status_param.split(',') if s.strip()]
            if statuses:
                queryset = queryset.filter(status__in=statuses)

        start_at = params.get('startAt')
        if start_at:
            queryset = queryset.filter(start_date__date=start_at)

        end_at = params.get('endAt')
        if end_at:
            queryset = queryset.filter(end_date__date=end_at)

        created_at = params.get('createdAt')
        if created_at:
            queryset = queryset.filter(created_at__date=created_at)

        return queryset

    def get(self, request):
        queryset = self._get_base_queryset()
        queryset = self._apply_filters(queryset)

        total = queryset.count()

        page = self._parse_positive_int(request.query_params.get('page', 1), 'page')
        page_size = min(
            self._parse_positive_int(
                request.query_params.get('page_size', self.DEFAULT_PAGE_SIZE),
                'page_size',
            ),
            self.MAX_PAGE_SIZE,
        )
        offset = (page - 1) * page_size
        page_queryset = queryset[offset:offset + page_size]

        return Response(
            TournamentListResponseSerializer(
                {'data': page_queryset, 'total': total},
                context={'request': request},  # ← додати це
            ).data,
        )


@extend_schema(
    operation_id='getTournament',
    responses={
        200: TournamentPublicSerializer,
        404: _404,
    },
)
class TournamentDetailView(SyncStatusesMixin, generics.RetrieveAPIView):
    queryset = get_tournament_queryset()
    permission_classes = [AllowAny]
    serializer_class = TournamentPublicSerializer

    def get_queryset(self):
        user = self.request.user
        base_queryset = get_tournament_queryset()
        published_filter = ~Q(status=Tournament.STATUS_DRAFT)

        if user_has_permission(user, Permission.VIEW_TOURNAMENT):
            return base_queryset

        if user.is_authenticated:
            return base_queryset.filter(published_filter | Q(created_by=user))

        return base_queryset.filter(published_filter)


@extend_schema(
    operation_id='createTournament',
    responses={
        201: TournamentPublicSerializer,
        400: _400,
        401: _401,
        403: _403,
    },
)
class TournamentCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, CanCreateTournament]
    serializer_class = TournamentAdminSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tournament = serializer.save()
        return Response(
            TournamentPublicSerializer(tournament, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


@extend_schema(methods=['GET'], operation_id='getTournamentForUpdate', responses={
    200: TournamentAdminSerializer,
    401: _401,
    403: _403,
    404: _404,
})
@extend_schema(methods=['PUT'], operation_id='replaceTournament', responses={
    200: TournamentPublicSerializer,
    400: _400,
    401: _401,
    403: _403,
    404: _404,
})
@extend_schema(methods=['PATCH'], operation_id='updateTournament', responses={
    200: TournamentPublicSerializer,
    400: _400,
    401: _401,
    403: _403,
    404: _404,
})
@extend_schema(methods=['DELETE'], operation_id='deleteTournament', responses={
    204: OpenApiResponse(description='Tournament deleted successfully.'),
    401: _401,
    403: _403,
    404: _404,
})
class TournamentUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tournament.objects.all()
    serializer_class = TournamentAdminSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.request.method == 'DELETE':
            permission_classes.append(CanDeleteTournament)
        elif self.request.method == 'GET':
            permission_classes.append(CanViewTournament)
        else:
            permission_classes.append(CanEditTournament)
        return [permission() for permission in permission_classes]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        tournament = self.get_object()
        serializer = self.get_serializer(tournament, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        tournament = serializer.save()
        return Response(
            TournamentPublicSerializer(tournament, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        tournament = self.get_object()
        tournament.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@extend_schema(methods=['PATCH'], operation_id='updateTournamentBanner', responses={
    200: TournamentPublicSerializer,
    400: _400,
    401: _401,
    403: _403,
    404: _404,
})
@extend_schema(methods=['DELETE'], operation_id='deleteTournamentBanner', responses={
    200: TournamentPublicSerializer,
    401: _401,
    403: _403,
    404: _404,
})
class TournamentBannerView(generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Tournament.objects.all()
    permission_classes = [IsAuthenticated, CanEditTournament]
    serializer_class = TournamentBannerSerializer
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        tournament = self.get_object()
        if tournament.banner:
            tournament.banner.delete(save=False)
            tournament.banner = None
            tournament.save(update_fields=['banner'])
        return Response(
            TournamentPublicSerializer(tournament, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )


@extend_schema(
    operation_id='startTournamentRegistration',
    request=None,
    responses={
        200: TournamentPublicSerializer,
        400: _400,
        401: _401,
        403: _403,
        404: _404,
    },
)
class TournamentStartRegistrationView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, CanEditTournament]
    serializer_class = TournamentPublicSerializer

    def post(self, request, pk):
        tournament = get_object_or_404(Tournament, pk=pk)
        start_registration(tournament)
        return Response(
            TournamentPublicSerializer(tournament, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )


@extend_schema(
    operation_id='registerTeamForTournament',
    responses={
        201: TournamentTeamRegistrationSerializer,
        400: _400,
        401: _401,
        403: _403,
        404: _404,
    },
)
class TournamentTeamRegistrationCreateView(SyncStatusesMixin, generics.GenericAPIView):
    permission_classes = [IsAuthenticated, CanRegisterTeamForTournament]
    serializer_class = TournamentTeamRegistrationCreateSerializer

    def post(self, request, pk):
        tournament = get_object_or_404(Tournament, pk=pk)
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request, 'tournament': tournament},
        )
        serializer.is_valid(raise_exception=True)
        registration = serializer.save()
        return Response(TournamentTeamRegistrationSerializer(registration).data, status=status.HTTP_201_CREATED)


@extend_schema(
    operation_id='unregisterTeamFromTournament',
    responses={
        200: TournamentTeamRegistrationSerializer,
        400: _400,
        401: _401,
        403: _403,
        404: _404,
    },
)
class TournamentTeamLeaveView(SyncStatusesMixin, generics.GenericAPIView):
    permission_classes = [IsAuthenticated, CanRegisterTeamForTournament]
    serializer_class = TournamentTeamLeaveSerializer

    def post(self, request, pk):
        tournament = get_object_or_404(Tournament, pk=pk)
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request, 'tournament': tournament},
        )
        serializer.is_valid(raise_exception=True)
        registration = serializer.save()
        return Response(TournamentTeamRegistrationSerializer(registration).data, status=status.HTTP_200_OK)


@extend_schema(
    operation_id='getTournamentTeamRegistration',
    responses={
        200: TournamentTeamRegistrationSerializer,
        401: _401,
        403: _403,
        404: _404,
    },
)
class TournamentTeamRegistrationDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, CanManageParticipants]
    serializer_class = TournamentTeamRegistrationSerializer

    def get_queryset(self):
        return TournamentTeamRegistration.objects.filter(
            tournament_id=self.kwargs['pk'],
        ).select_related('team')

    def get_object(self):
        queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.kwargs['registration_pk'])


@extend_schema(
    operation_id='disqualifyTeamFromTournament',
    responses={
        200: DisqualificationResponseSerializer,
        400: _400,
        401: _401,
        403: _403,
        404: _404,
    },
)
class TournamentTeamRegistrationDisqualificationView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, CanManageParticipants]
    serializer_class = TournamentTeamRegistrationDisqualificationSerializer

    def patch(self, request, pk, registration_pk):
        registration = get_object_or_404(
            TournamentTeamRegistration.objects.filter(tournament_id=pk).select_related('team'),
            pk=registration_pk,
        )
        serializer = self.get_serializer(registration, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        action = 'activated' if registration.is_active else 'disqualified'

        return Response(
            DisqualificationResponseSerializer({
                'id': registration.id,
                'team_id': registration.team_id,
                'team_name': registration.team.name,
                'tournament_id': registration.tournament_id,
                'is_active': registration.is_active,
                'action': action,
            }).data,
        )


@extend_schema(
    operation_id='listEligibleTeamsForTournament',
    responses={
        200: EligibleTeamSerializer(many=True),
        401: _401,
        404: _404,
    },
)
class TournamentEligibleTeamsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EligibleTeamSerializer

    def get(self, request, pk):
        get_object_or_404(Tournament, pk=pk)
        teams = (
            Team.objects.filter(captain_id=request.user.id)
            .annotate(members_count=Count('team_members', distinct=True))
            .values('id', 'name', 'members_count')
            .order_by('id')
        )
        return Response(EligibleTeamSerializer(list(teams), many=True).data, status=status.HTTP_200_OK)


@extend_schema(
    operation_id='listTournamentTeams',
    parameters=[
        OpenApiParameter('status', OpenApiTypes.STR, required=False, description='all | disqualified | active (default)'),
    ],
    responses={
        200: TournamentTeamRegistrationListSerializer(many=True),
        401: _401,
        403: _403,
        404: _404,
    },
)
class TournamentTeamsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TournamentTeamRegistrationListSerializer

    def get(self, request, pk):
        get_object_or_404(Tournament, pk=pk)

        queryset = TournamentTeamRegistration.objects.filter(
            tournament_id=pk,
        ).select_related('team', 'team__captain').prefetch_related('team__members')

        status_filter = request.query_params.get('status')
        if status_filter == 'disqualified':
            queryset = queryset.filter(is_disqualified=True)
        elif status_filter == 'all':
            pass
        else:
            queryset = queryset.filter(is_active=True)

        return Response(
            TournamentTeamRegistrationListSerializer(queryset.order_by('id'), many=True).data,
            status=status.HTTP_200_OK,
        )


@extend_schema(
    operation_id='getTeamActiveTournament',
    parameters=[
        OpenApiParameter('team_id', OpenApiTypes.INT, required=True),
    ],
    responses={
        200: ActiveTournamentSerializer,
        401: _401,
        404: _404,
    },
)
class TeamActiveTournamentView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ActiveTournamentSerializer

    def get(self, request):
        team_id = request.query_params.get('team_id')
        registration = (
            TournamentTeamRegistration.objects.select_related('tournament')
            .filter(
                team_id=team_id,
                tournament__status__in=[
                    Tournament.STATUS_REGISTRATION,
                    Tournament.STATUS_RUNNING,
                ],
                is_active=True,
            )
            .first()
        )
        if registration is None:
            raise NotFound('Active tournament not found for this team.')

        return Response(
            ActiveTournamentSerializer(registration.tournament).data,
            status=status.HTTP_200_OK,
        )


@extend_schema(methods=['GET'], operation_id='listRounds',
    parameters=[
        OpenApiParameter('status', OpenApiTypes.STR, required=False, description='Comma-separated statuses'),
    ],
    responses={
        200: RoundSerializer(many=True),
        401: _401,
        403: _403,
        404: _404,
    },
)
@extend_schema(methods=['POST'], operation_id='createRound', responses={
    201: RoundSerializer,
    400: _400,
    401: _401,
    403: _403,
    404: _404,
})
class RoundListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, CanManageRoundsOrReadOnly]
    serializer_class = RoundSerializer

    def _get_tournament(self):
        if hasattr(self, '_tournament'):
            return self._tournament
        self._tournament = get_object_or_404(Tournament, pk=self.kwargs['tournament_pk'])
        return self._tournament

    def get_queryset(self):
        tournament = self._get_tournament()
        queryset = get_round_queryset().filter(tournament_id=tournament.id)
        user = self.request.user

        can_view_draft = user_has_permission(user, Permission.VIEW_TOURNAMENT)
        if not can_view_draft:
            can_view_draft = TournamentTeamRegistration.objects.filter(
                tournament_id=tournament.id,
                is_active=True,
            ).filter(
                Q(team__captain_id=user.id) | Q(team__team_members__user_id=user.id),
            ).exists()

        if not can_view_draft:
            queryset = queryset.exclude(status=Round.STATUS_DRAFT)

        status_param = self.request.query_params.get('status')
        if status_param:
            statuses = [s.strip() for s in status_param.split(',') if s.strip()]
            if statuses:
                queryset = queryset.filter(status__in=statuses)

        return queryset

    def perform_create(self, serializer):
        tournament = self._get_tournament()
        request_tournament = serializer.validated_data.get('tournament')
        if request_tournament and request_tournament.id != tournament.id:
            raise ValidationError({'tournament': 'Tournament in URL and payload must match.'})
        serializer.save(tournament=tournament)

    def create(self, request, *args, **kwargs):
        tournament = self._get_tournament()
        data = request.data.copy()
        if hasattr(data, 'setdefault'):
            data.setdefault('tournament', tournament.id)
        else:
            data = {**data, 'tournament': tournament.id}

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


@extend_schema(methods=['GET'], operation_id='getRound', responses={
    200: RoundSerializer,
    401: _401,
    403: _403,
    404: _404,
})
@extend_schema(methods=['PUT'], operation_id='replaceRound', responses={
    200: RoundSerializer,
    400: _400,
    401: _401,
    403: _403,
    404: _404,
})
@extend_schema(methods=['PATCH'], operation_id='updateRound', responses={
    200: RoundSerializer,
    400: _400,
    401: _401,
    403: _403,
    404: _404,
})
@extend_schema(methods=['DELETE'], operation_id='deleteRound', responses={
    204: OpenApiResponse(description='Round deleted successfully.'),
    401: _401,
    403: _403,
    404: _404,
})
class RoundDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, CanManageRoundsOrReadOnly]
    serializer_class = RoundSerializer

    def get_queryset(self):
        queryset = get_round_queryset()
        user = self.request.user

        if not user_has_permission(user, Permission.VIEW_TOURNAMENT):
            queryset = queryset.exclude(status=Round.STATUS_DRAFT)

        return queryset

    def destroy(self, request, *args, **kwargs):
        round_obj = self.get_object()
        delete_round(round_obj)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    operation_id='startRound',
    request=None,
    responses={
        200: RoundSerializer,
        400: _400,
        401: _401,
        403: _403,
        404: _404,
    },
)
class RoundStartView(SyncStatusesMixin, generics.GenericAPIView):
    permission_classes = [IsAuthenticated, CanManageRounds]
    serializer_class = RoundSerializer

    def post(self, request, pk):
        round_obj = get_object_or_404(get_round_queryset(), pk=pk)
        start_round(round_obj)
        round_obj.refresh_from_db()
        return Response(RoundSerializer(round_obj).data, status=status.HTTP_200_OK)


@extend_schema(
    operation_id='markRoundEvaluated',
    request=None,
    responses={
        200: RoundSerializer,
        400: _400,
        401: _401,
        403: _403,
        404: _404,
    },
)
class RoundMarkEvaluatedView(SyncStatusesMixin, generics.GenericAPIView):
    permission_classes = [IsAuthenticated, CanSetResults]
    serializer_class = RoundSerializer

    def post(self, request, pk):
        round_obj = get_object_or_404(get_round_queryset(), pk=pk)
        mark_round_evaluated(round_obj)
        round_obj.refresh_from_db()
        return Response(RoundSerializer(round_obj).data, status=status.HTTP_200_OK)


@extend_schema(
    operation_id='listTournamentSubmissions',
    responses={
        200: SubmissionSerializer(many=True),
        401: _401,
        404: _404,
    },
)
class TournamentSubmissionsView(SyncStatusesMixin, generics.ListAPIView):
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        tournament = get_object_or_404(Tournament, pk=self.kwargs['pk'])
        return (
            Submission.objects.select_related('team', 'round', 'round__tournament')
            .prefetch_related('jury_assignments__jury', 'jury_assignments__evaluation')
            .filter(round__tournament=tournament)
            .exclude(
                team__tournament_registrations__tournament=tournament,
                team__tournament_registrations__is_disqualified=True,
            )
            .order_by('-updated_at')
        )


@extend_schema(
    operation_id='listMyTeamSubmissions',
    responses={
        200: SubmissionSerializer(many=True),
        401: _401,
        404: _404,
    },
)
class TournamentMyTeamSubmissionsView(SyncStatusesMixin, generics.ListAPIView):
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        tournament = get_object_or_404(Tournament, pk=self.kwargs['pk'])

        team_registration = (
            TournamentTeamRegistration.objects.select_related('team')
            .filter(
                tournament=tournament,
                is_active=True,
            )
            .filter(
                Q(team__captain_id=user.id) | Q(team__team_members__user_id=user.id),
            )
            .first()
        )
        if team_registration is None:
            raise NotFound('No team participation found for this tournament.')

        return (
            Submission.objects.select_related('team', 'round', 'round__tournament')
            .prefetch_related('jury_assignments__jury', 'jury_assignments__evaluation')
            .filter(
                round__tournament=tournament,
                team_id=team_registration.team_id,
            )
            .order_by('-updated_at')
        )


@extend_schema(
    operation_id='listRoundSubmissions',
    responses={
        200: SubmissionSerializer(many=True),
        401: _401,
        403: _403,
        404: _404,
    },
)
class RoundSubmissionsView(SyncStatusesMixin, generics.ListAPIView):
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated, CanSetResults]

    def get_queryset(self):
        round_obj = get_object_or_404(Round, pk=self.kwargs['pk'])
        return (
            Submission.objects.select_related('team', 'round', 'round__tournament')
            .prefetch_related('jury_assignments__jury')
            .filter(round=round_obj)
            .exclude(
                team__tournament_registrations__tournament=round_obj.tournament,
                team__tournament_registrations__is_disqualified=True,
            )
            .order_by('-updated_at')
        )


@extend_schema(
    operation_id='closeRoundSubmissions',
    request=None,
    responses={
        200: RoundSerializer,
        400: _400,
        401: _401,
        403: _403,
        404: _404,
    },
)
class RoundCloseSubmissionsView(SyncStatusesMixin, generics.GenericAPIView):
    permission_classes = [IsAuthenticated, CanManageRounds]
    serializer_class = RoundSerializer

    def post(self, request, pk):
        round_obj = get_object_or_404(get_round_queryset(), pk=pk)
        close_submissions_on_round(round_obj)
        round_obj.refresh_from_db()
        return Response(RoundSerializer(round_obj).data, status=status.HTTP_200_OK)


@extend_schema(methods=['GET'], operation_id='listSubmissions', responses={
    200: OwnSubmissionSerializer(many=True),
    401: _401,
})
@extend_schema(methods=['POST'], operation_id='createSubmission', responses={
    201: SubmissionSerializer,
    400: _400,
    401: _401,
})
class SubmissionListCreateView(SyncStatusesMixin, generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OwnSubmissionSerializer
        return SubmissionSerializer

    def get_queryset(self):
        return get_own_submissions_queryset(self.request.user)


@extend_schema(methods=['GET'], operation_id='getSubmission', responses={
    200: OwnSubmissionSerializer,
    401: _401,
    404: _404,
})
@extend_schema(methods=['PUT'], operation_id='replaceSubmission', responses={
    200: SubmissionSerializer,
    400: _400,
    401: _401,
    403: _403,
    404: _404,
})
@extend_schema(methods=['PATCH'], operation_id='updateSubmission', responses={
    200: SubmissionSerializer,
    400: _400,
    401: _401,
    403: _403,
    404: _404,
})
class SubmissionDetailView(SyncStatusesMixin, generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OwnSubmissionSerializer
        return SubmissionSerializer

    def get_queryset(self):
        return get_own_submissions_queryset(self.request.user)


@extend_schema(
    operation_id='getCurrentTask',
    parameters=[
        OpenApiParameter('tournament_id', OpenApiTypes.INT, required=False),
    ],
    responses={
        200: CurrentTaskSerializer,
        401: _401,
        403: _403,
        404: _404,
    },
)
class CurrentTaskView(SyncStatusesMixin, generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsPlatformAdminOrTeamMemberPermission]
    serializer_class = CurrentTaskSerializer

    def get(self, request):
        queryset = (
            Round.objects.select_related('tournament')
            .filter(
                status=Round.STATUS_ACTIVE,
                tournament__status=Tournament.STATUS_RUNNING,
            )
            .order_by('end_date', 'id')
        )

        tournament_id = request.query_params.get('tournament_id')
        if tournament_id:
            queryset = queryset.filter(tournament_id=tournament_id)

        active_round = queryset.first()
        if not active_round:
            raise NotFound('No active round is available right now.')

        return Response(CurrentTaskSerializer(active_round).data, status=status.HTTP_200_OK)


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [CanManageRoundsOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    @extend_schema(
        operation_id='listEvents',
        parameters=[
            OpenApiParameter('tournament', OpenApiTypes.INT, required=False),
        ],
        responses={
            200: EventSerializer(many=True),
            401: _401,
            403: _403,
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(operation_id='createEvent', responses={
        201: EventSerializer,
        400: _400,
        401: _401,
        403: _403,
    })
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(operation_id='getEvent', responses={
        200: EventSerializer,
        401: _401,
        403: _403,
        404: _404,
    })
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(operation_id='updateEvent', responses={
        200: EventSerializer,
        400: _400,
        401: _401,
        403: _403,
        404: _404,
    })
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(operation_id='deleteEvent', responses={
        204: OpenApiResponse(description='Event deleted successfully.'),
        401: _401,
        403: _403,
        404: _404,
    })
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Event.objects.select_related('icon', 'tournament').order_by('start_datetime')
        tournament_id = self.request.query_params.get('tournament')
        if tournament_id:
            queryset = queryset.filter(tournament_id=tournament_id)
        return queryset

@extend_schema(
    operation_id='getMyCalendar',
    responses={
        200: inline_serializer(
            name='MyCalendarResponse',
            fields={
                'events': EventSerializer(many=True),
                'rounds': RoundSerializer(many=True),
            }
        ),
        401: _401,
    },
)
class MyCalendarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user_has_permission(user, Permission.VIEW_TOURNAMENT):
            tournament_ids = Tournament.objects.exclude(
                status=Tournament.STATUS_DRAFT
            ).values_list('id', flat=True)
        else:
            tournament_ids = TournamentTeamRegistration.objects.filter(
                is_active=True,
            ).filter(
                Q(team__captain_id=user.id) | Q(team__team_members__user_id=user.id),
            ).values_list('tournament_id', flat=True)

        events = (
            Event.objects.select_related('icon', 'tournament')
            .filter(tournament_id__in=tournament_ids)
            .order_by('start_datetime')
        )
        rounds = (
            Round.objects.select_related('tournament')
            .filter(tournament_id__in=tournament_ids)
            .order_by('start_date')
        )

        return Response({
            'events': EventSerializer(events, many=True).data,
            'rounds': RoundSerializer(rounds, many=True).data,
        })

@extend_schema(
    operation_id='listIcons',
    responses={
        200: IconSerializer(many=True),
    },
)
class IconListView(generics.ListAPIView):
    queryset = Icon.objects.all()
    serializer_class = IconSerializer
    permission_classes = [AllowAny]

@extend_schema(
    operation_id='listTournamentArchive',
    responses={
        200: TournamentArchiveListSerializer(many=True),
    },
)
class TournamentArchiveListView(SyncStatusesMixin, generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = TournamentArchiveListSerializer

    def get_queryset(self):
        return (
            Tournament.objects.filter(status=Tournament.STATUS_FINISHED)
            .prefetch_related(
                Prefetch('rounds', queryset=Round.objects.order_by('start_date')),
                'team_registrations__team',
                'leaderboard_entries__team',
            )
            .order_by('-end_date', '-created_at')
        )

@extend_schema(
    operation_id='getTournamentArchive',
    responses={
        200: TournamentArchiveDetailSerializer,
        404: _404,
    },
)
class TournamentArchiveDetailView(SyncStatusesMixin, generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = TournamentArchiveDetailSerializer

    def get_queryset(self):
        return (
            Tournament.objects.filter(status=Tournament.STATUS_FINISHED)
            .prefetch_related(
                Prefetch('rounds', queryset=Round.objects.order_by('start_date')),
                'team_registrations__team',
                'leaderboard_entries__team',
            )
        )

@extend_schema(
    operation_id='listTournamentArchiveSubmissions',
    responses={
        200: SubmissionSerializer(many=True),
        401: _401,
        404: _404,
    },
)
class TournamentArchiveSubmissionsView(SyncStatusesMixin, generics.ListAPIView):
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        tournament = get_object_or_404(
            Tournament.objects.filter(status=Tournament.STATUS_FINISHED),
            pk=self.kwargs['pk'],
        )
        return (
            Submission.objects.select_related('team', 'round', 'round__tournament')
            .prefetch_related('jury_assignments__jury', 'jury_assignments__evaluation')
            .filter(round__tournament=tournament)
            .exclude(
                team__tournament_registrations__tournament=tournament,
                team__tournament_registrations__is_disqualified=True,
            )
            .order_by('-updated_at')
        )
