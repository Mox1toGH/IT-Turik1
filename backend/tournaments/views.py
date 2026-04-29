from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Round, Submission, Tournament
from .permissions import (
    CanCreateTournamentPermission,
    IsJuryPermission,
    IsPlatformAdminOrTeamMemberPermission,
    IsPlatformAdminPermission,
)
from .serializers import (
    CurrentTaskSerializer,
    
    OwnSubmissionSerializer,
    RoundSerializer,
    
    SubmissionSerializer,
    TournamentAdminSerializer,
    TournamentPublicSerializer,
    TournamentTeamRegistrationCreateSerializer,
    TournamentTeamRegistrationSerializer,
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
        Prefetch('rounds', queryset=Round.objects.order_by('position'))
    ).order_by('-created_at')


def get_round_queryset():
    return Round.objects.select_related('tournament').order_by('tournament_id', 'position')


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


class TournamentListView(SyncStatusesMixin, generics.ListAPIView):
    queryset = get_tournament_queryset()
    permission_classes = [AllowAny]
    serializer_class = TournamentPublicSerializer

    def get_queryset(self):
        user = self.request.user
        base_queryset = get_tournament_queryset()
        published_filter = ~Q(status=Tournament.STATUS_DRAFT)

        if user.is_staff:
            return base_queryset

        if user.is_authenticated:
            return base_queryset.filter(published_filter | Q(created_by=user))

        return base_queryset.filter(published_filter)


class TournamentDetailView(SyncStatusesMixin, generics.RetrieveAPIView):
    queryset = get_tournament_queryset()
    permission_classes = [AllowAny]
    serializer_class = TournamentPublicSerializer

    def get_queryset(self):
        user = self.request.user
        base_queryset = get_tournament_queryset()
        published_filter = ~Q(status=Tournament.STATUS_DRAFT)

        if user.is_staff:
            return base_queryset

        if user.is_authenticated:
            return base_queryset.filter(published_filter | Q(created_by=user))

        return base_queryset.filter(published_filter)


class TournamentCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, CanCreateTournamentPermission]
    serializer_class = TournamentAdminSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tournament = serializer.save()
        return Response(TournamentPublicSerializer(tournament).data, status=status.HTTP_201_CREATED)


class TournamentUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tournament.objects.all()
    permission_classes = [IsAuthenticated, IsPlatformAdminPermission]
    serializer_class = TournamentAdminSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        tournament = self.get_object()
        serializer = self.get_serializer(tournament, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        tournament = serializer.save()
        return Response(TournamentPublicSerializer(tournament).data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        tournament = self.get_object()
        if tournament.created_by_id != request.user.id:
            raise PermissionDenied('Only the admin owner of this tournament can delete it.')
        tournament.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TournamentStartRegistrationView(APIView):
    permission_classes = [IsAuthenticated, IsPlatformAdminPermission]

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


class RoundListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsPlatformAdminPermission]
    serializer_class = RoundSerializer

    def get_queryset(self):
        queryset = get_round_queryset()
        tournament_id = self.request.query_params.get('tournament_id')
        if tournament_id:
            queryset = queryset.filter(tournament_id=tournament_id)
        return queryset


class RoundDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsPlatformAdminPermission]
    serializer_class = RoundSerializer

    def get_queryset(self):
        return get_round_queryset()

    def destroy(self, request, *args, **kwargs):
        round_obj = self.get_object()
        delete_round(round_obj)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RoundStartView(SyncStatusesMixin, APIView):
    permission_classes = [IsAuthenticated, IsPlatformAdminPermission]

    def post(self, request, pk):
        round_obj = get_object_or_404(get_round_queryset(), pk=pk)
        start_round(round_obj)
        round_obj.refresh_from_db()
        return Response(RoundSerializer(round_obj).data, status=status.HTTP_200_OK)


class RoundMarkEvaluatedView(SyncStatusesMixin, APIView):
    permission_classes = [IsAuthenticated, IsPlatformAdminPermission]

    def post(self, request, pk):
        round_obj = get_object_or_404(get_round_queryset(), pk=pk)
        mark_round_evaluated(round_obj)
        round_obj.refresh_from_db()
        return Response(RoundSerializer(round_obj).data, status=status.HTTP_200_OK)


class RoundCloseSubmissionsView(SyncStatusesMixin, APIView):
    permission_classes = [IsAuthenticated, IsPlatformAdminPermission]

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


