from django.db.models import Count, IntegerField, Prefetch, Q, Value
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, viewsets
from rest_framework.exceptions import NotFound, ValidationError
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
    CanSetResults,
    CanViewTournament,
    IsPlatformAdminOrTeamMemberPermission,
)
from .serializers import (
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
    TournamentTeamRegistrationListSerializer,
    TournamentTeamRegistrationSerializer,
    TournamentTeamRegistrationUpdateSerializer,
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

        serializer = TournamentPublicSerializer(page_queryset, many=True)
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
        return Response(TournamentPublicSerializer(tournament).data, status=status.HTTP_201_CREATED)


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
        return Response(TournamentPublicSerializer(tournament).data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        tournament = self.get_object()
        tournament.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TournamentStartRegistrationView(APIView):
    permission_classes = [IsAuthenticated, CanEditTournament]

    def post(self, request, pk):
        tournament = get_object_or_404(Tournament, pk=pk)
        start_registration(tournament)
        return Response(TournamentPublicSerializer(tournament).data, status=status.HTTP_200_OK)


class TournamentTeamRegistrationCreateView(SyncStatusesMixin, APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        tournament = get_object_or_404(Tournament, pk=pk)
        serializer = TournamentTeamRegistrationCreateSerializer(
            data=request.data,
            context={'request': request, 'tournament': tournament},
        )
        serializer.is_valid(raise_exception=True)
        registration = serializer.save()
        return Response(TournamentTeamRegistrationSerializer(registration).data, status=status.HTTP_201_CREATED)


class TournamentTeamRegistrationDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, CanManageParticipants]

    def get_queryset(self):
        return TournamentTeamRegistration.objects.filter(
            tournament_id=self.kwargs['pk'],
        ).select_related('team')

    def get_object(self):
        queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.kwargs['registration_pk'])

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TournamentTeamRegistrationSerializer
        return TournamentTeamRegistrationUpdateSerializer


class TournamentEligibleTeamsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        get_object_or_404(Tournament, pk=pk)
        teams = (
            Team.objects.filter(captain_id=request.user.id)
            .annotate(
                members_count=Count('team_members', distinct=True) + Value(1, output_field=IntegerField())
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
        ).select_related('team').prefetch_related('team__team_members')
 
        only_active = request.query_params.get('only_active')
        if only_active and only_active.lower() == 'true':
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


class IconListView(generics.ListAPIView):
    queryset = Icon.objects.all()
    serializer_class = IconSerializer
    permission_classes = [AllowAny]
