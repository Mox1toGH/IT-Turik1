from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, viewsets
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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
    EventSerializer,
    IconSerializer,
    OwnSubmissionSerializer,
    RoundSerializer,
    SubmissionSerializer,
    TournamentAdminSerializer,
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
    get_tournament_certificate_delivery_status,
    mark_round_evaluated,
    send_tournament_certificates,
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


class TournamentListView(SyncStatusesMixin, APIView):
    permission_classes = [AllowAny]
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
                request.query_params.get('pageSize', self.DEFAULT_PAGE_SIZE),
                'pageSize',
            ),
            self.MAX_PAGE_SIZE,
        )
        offset = (page - 1) * page_size
        page_queryset = queryset[offset:offset + page_size]

        serializer = TournamentPublicSerializer(
            page_queryset,
            many=True,
            context={'request': request},
        )
        return Response({'data': serializer.data, 'total': total})


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


class TournamentStartRegistrationView(APIView):
    permission_classes = [IsAuthenticated, CanEditTournament]

    def post(self, request, pk):
        tournament = get_object_or_404(Tournament, pk=pk)
        start_registration(tournament)
        return Response(
            TournamentPublicSerializer(tournament, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )


class TournamentSendCertificatesView(APIView):
    permission_classes = [IsAuthenticated, CanEditTournament]

    def post(self, request, pk):
        tournament = get_object_or_404(Tournament, pk=pk)
        template_id = request.data.get('template_id')
        mode = request.data.get('mode', 'missing')
        if template_id is None:
            raise ValidationError({'template_id': 'This field is required.'})

        stats = send_tournament_certificates(
            tournament=tournament,
            template_id=template_id,
            mode=mode,
            async_notifications=True,
        )
        return Response(stats, status=status.HTTP_200_OK)

    def get(self, request, pk):
        tournament = get_object_or_404(Tournament, pk=pk)
        stats = get_tournament_certificate_delivery_status(tournament=tournament)
        return Response(stats, status=status.HTTP_200_OK)


class TournamentTeamRegistrationCreateView(SyncStatusesMixin, APIView):
    permission_classes = [IsAuthenticated, CanRegisterTeamForTournament]

    def post(self, request, pk):
        tournament = get_object_or_404(Tournament, pk=pk)
        serializer = TournamentTeamRegistrationCreateSerializer(
            data=request.data,
            context={'request': request, 'tournament': tournament},
        )
        serializer.is_valid(raise_exception=True)
        registration = serializer.save()
        return Response(TournamentTeamRegistrationSerializer(registration).data, status=status.HTTP_201_CREATED)


class TournamentTeamLeaveView(SyncStatusesMixin, APIView):
    permission_classes = [IsAuthenticated, CanRegisterTeamForTournament]

    def post(self, request, pk):
        tournament = get_object_or_404(Tournament, pk=pk)
        serializer = TournamentTeamLeaveSerializer(
            data=request.data,
            context={'request': request, 'tournament': tournament},
        )
        serializer.is_valid(raise_exception=True)
        registration = serializer.save()
        return Response(TournamentTeamRegistrationSerializer(registration).data, status=status.HTTP_200_OK)


class TournamentTeamRegistrationDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, CanManageParticipants]

    def get_queryset(self):
        return TournamentTeamRegistration.objects.filter(
            tournament_id=self.kwargs['pk'],
        ).select_related('team')

    def get_object(self):
        queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.kwargs['registration_pk'])

    serializer_class = TournamentTeamRegistrationSerializer


class TournamentTeamRegistrationDisqualificationView(APIView):
    permission_classes = [IsAuthenticated, CanManageParticipants]

    def patch(self, request, pk, registration_pk):
        registration = get_object_or_404(
            TournamentTeamRegistration.objects.filter(tournament_id=pk).select_related('team'),
            pk=registration_pk,
        )
        serializer = TournamentTeamRegistrationDisqualificationSerializer(
            registration,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        action = 'activated' if registration.is_active else 'disqualified'

        return Response({
            'id': registration.id,
            'team_id': registration.team_id,
            'team_name': registration.team.name,
            'tournament_id': registration.tournament_id,
            'is_active': registration.is_active,
            'action': action,
        })


class TournamentEligibleTeamsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        get_object_or_404(Tournament, pk=pk)
        teams = (
            Team.objects.filter(captain_id=request.user.id)
            .annotate(
                members_count=Count('team_members', distinct=True)
            )
            .values('id', 'name', 'members_count')
            .order_by('id')
        )
        return Response(list(teams), status=status.HTTP_200_OK)


class TournamentTeamsView(APIView):
    permission_classes = [IsAuthenticated]
 
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
            # Default: return only active teams (active=True, disqualified=False)
            queryset = queryset.filter(is_active=True)
 
        serializer = TournamentTeamRegistrationListSerializer(queryset.order_by('id'), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TeamActiveTournamentView(APIView):
    permission_classes = [IsAuthenticated]

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

        serializer = ActiveTournamentSerializer(registration.tournament)
        return Response(serializer.data, status=status.HTTP_200_OK)


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

        if not user_has_permission(user, Permission.VIEW_TOURNAMENT):
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


class RoundStartView(SyncStatusesMixin, APIView):
    permission_classes = [IsAuthenticated, CanManageRounds]

    def post(self, request, pk):
        round_obj = get_object_or_404(get_round_queryset(), pk=pk)
        start_round(round_obj)
        round_obj.refresh_from_db()
        return Response(RoundSerializer(round_obj).data, status=status.HTTP_200_OK)


class RoundMarkEvaluatedView(SyncStatusesMixin, APIView):
    permission_classes = [IsAuthenticated, CanSetResults]

    def post(self, request, pk):
        round_obj = get_object_or_404(get_round_queryset(), pk=pk)
        mark_round_evaluated(round_obj)
        round_obj.refresh_from_db()
        return Response(RoundSerializer(round_obj).data, status=status.HTTP_200_OK)


class TournamentSubmissionsView(SyncStatusesMixin, generics.ListAPIView):
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        tournament = get_object_or_404(Tournament, pk=self.kwargs['pk'])
        return (
            Submission.objects.select_related('team', 'round', 'round__tournament')
            .prefetch_related('jury_assignments__jury', 'jury_assignments__evaluation')
            .filter(round__tournament=tournament)
            .exclude(team__tournament_registrations__tournament=tournament, team__tournament_registrations__is_disqualified=True)
            .order_by('-updated_at')
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

class RoundCloseSubmissionsView(SyncStatusesMixin, APIView):
    permission_classes = [IsAuthenticated, CanManageRounds]

    def post(self, request, pk):
        round_obj = get_object_or_404(get_round_queryset(), pk=pk)
        close_submissions_on_round(round_obj)
        round_obj.refresh_from_db()
        return Response(RoundSerializer(round_obj).data, status=status.HTTP_200_OK)


class SubmissionListCreateView(SyncStatusesMixin, generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OwnSubmissionSerializer
        return SubmissionSerializer

    def get_queryset(self):
        return get_own_submissions_queryset(self.request.user)


class SubmissionDetailView(SyncStatusesMixin, generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OwnSubmissionSerializer
        return SubmissionSerializer

    def get_queryset(self):
        return get_own_submissions_queryset(self.request.user)


class CurrentTaskView(SyncStatusesMixin, APIView):
    permission_classes = [IsAuthenticated, IsPlatformAdminOrTeamMemberPermission]

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

    def get_queryset(self):
        queryset = Event.objects.select_related('icon', 'tournament').order_by('start_datetime')
        tournament_id = self.request.query_params.get('tournament')
        if tournament_id:
            queryset = queryset.filter(tournament_id=tournament_id)
        return queryset


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


class IconListView(generics.ListAPIView):
    queryset = Icon.objects.all()
    serializer_class = IconSerializer
    permission_classes = [AllowAny]


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
