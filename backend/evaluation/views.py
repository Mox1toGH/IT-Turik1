from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from tournaments.models import Round
from tournaments.permissions import CanManageAssignments, CanSetResults
from .services import get_available_jury, replace_round_jury_assignments, try_auto_evaluate_round
from .leaderboard_service import get_leaderboard, get_tournament_leaderboard

from .models import JuryAssignment, SubmissionEvaluation
from .serializers import (
    AvailableJurySerializer,
    JuryAssignmentItemSerializer,
    JuryAssignmentSerializer,
    SubmissionEvaluationSerializer,
)


class JuryAssignmentListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, CanSetResults]
    serializer_class = JuryAssignmentSerializer

    def get_queryset(self):
        return JuryAssignment.objects.filter(jury=self.request.user).select_related(
            'submission', 'submission__team', 'submission__round', 'submission__round__tournament'
        )


class JuryEvaluationCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, CanSetResults]
    serializer_class = SubmissionEvaluationSerializer

    def perform_create(self, serializer):
        serializer.save()
        round_obj = serializer.instance.assignment.submission.round
        try_auto_evaluate_round(round_obj)


class JuryEvaluationDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, CanSetResults]
    serializer_class = SubmissionEvaluationSerializer
    lookup_field = 'assignment_id'

    def get_queryset(self):
        return SubmissionEvaluation.objects.filter(assignment__jury=self.request.user)

    def perform_update(self, serializer):
        serializer.save()
        round_obj = serializer.instance.assignment.submission.round
        try_auto_evaluate_round(round_obj)


class AdminRoundAssignmentView(APIView):
    permission_classes = [IsAuthenticated, CanManageAssignments]

    def post(self, request, pk):
        round_obj = get_object_or_404(Round, pk=pk)
        serializer = JuryAssignmentItemSerializer(data=request.data, many=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        created_count = replace_round_jury_assignments(round_obj, serializer.validated_data)
        return Response(
            {'status': 'Assignments replaced.', 'created_assignments': created_count},
            status=status.HTTP_201_CREATED,
        )


class AvailableJuryListView(APIView):
    permission_classes = [IsAuthenticated, CanManageAssignments]

    def get(self, request, pk):
        round_obj = get_object_or_404(Round, pk=pk)
        include_assigned_param = request.query_params.get('include_assigned', 'true').lower()
        if include_assigned_param not in {'true', 'false'}:
            raise ValidationError({'include_assigned': 'Expected "true" or "false".'})

        include_assigned = include_assigned_param == 'true'
        jury_queryset = get_available_jury(round_obj=round_obj, include_assigned=include_assigned)
        return Response(AvailableJurySerializer(jury_queryset, many=True).data, status=status.HTTP_200_OK)


class RoundLeaderboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, round_id):
        round_obj = Round.objects.select_related('tournament').filter(id=round_id).first()
        if not round_obj:
            raise NotFound('Round not found.')

        rankings = get_leaderboard(round_id=round_id, requesting_user=request.user)
        is_snapshot = round_obj.tournament.status == Tournament.STATUS_FINISHED

        return Response(
            {
                'round_id': round_id,
                'is_snapshot': is_snapshot,
                'rankings': rankings,
            },
            status=status.HTTP_200_OK,
        )


class TournamentLeaderboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, tournament_id):
        tournament = Tournament.objects.filter(id=tournament_id).first()
        if not tournament:
            raise NotFound('Tournament not found.')

        has_rounds = Round.objects.filter(tournament_id=tournament_id).exists()
        if not has_rounds:
            raise NotFound('No rounds found for this tournament.')

        rankings = get_tournament_leaderboard(tournament_id=tournament_id, requesting_user=request.user)
        is_snapshot = tournament.status == Tournament.STATUS_FINISHED

        return Response(
            {
                'tournament_id': tournament_id,
                'is_snapshot': is_snapshot,
                'rankings': rankings,
            },
            status=status.HTTP_200_OK,
        )
