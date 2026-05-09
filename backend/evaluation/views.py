from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from tournaments.models import Round, Tournament, TournamentTeamRegistration
from tournaments.permissions import CanManageAssignments, CanSetResults
from .services import get_available_jury, replace_round_jury_assignments, try_auto_evaluate_round
from .leaderboard_service import compute_leaderboard, get_leaderboard, get_tournament_leaderboard

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
        qs = JuryAssignment.objects.filter(jury=self.request.user).select_related(
            'submission', 'submission__team', 'submission__round', 'submission__round__tournament'
        )
        round_id = self.request.query_params.get('round_id')
        if round_id:
            qs = qs.filter(submission__round_id=round_id)
        return qs


class JuryAssignmentDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, CanSetResults]
    serializer_class = JuryAssignmentSerializer

    def get_queryset(self):
        return JuryAssignment.objects.filter(
            jury=self.request.user
        ).select_related(
            'submission',
            'submission__team',
            'submission__round',
            'submission__round__tournament',
        ).prefetch_related('evaluation')


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
    lookup_field = 'pk'

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
        self.check_object_permissions(request, round_obj)
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
        self.check_object_permissions(request, round_obj)
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


class RoundPassingStatusView(APIView):
    permission_classes = [IsAuthenticated, CanManageAssignments]

    def get(self, request, pk):
        round_obj = get_object_or_404(Round.objects.select_related('tournament'), pk=pk)
        self.check_object_permissions(request, round_obj)

        if round_obj.status not in {Round.STATUS_SUBMISSION_CLOSED, Round.STATUS_EVALUATED}:
            raise ValidationError({'status': 'Round must be submission_closed or evaluated to check passing status.'})

        result = compute_leaderboard(round_obj.id)
        team_ids = [row['team_id'] for row in result]

        registrations = {
            reg.team_id: reg
            for reg in TournamentTeamRegistration.objects.filter(
                tournament=round_obj.tournament,
                team_id__in=team_ids,
            )
        }

        passing_count = round_obj.passing_count

        results_list = []
        for row in result:
            passed = (
                passing_count is None
                or row['rank'] <= passing_count
            )
            reg = registrations.get(row['team_id'])

            results_list.append({
                'rank': row['rank'],
                'team_id': row['team_id'],
                'team_name': row['team_name'],
                'total_score': row['total_score'],
                'average_score': row['average_score'],
                'passed': passed,
                'is_active': reg.is_active if reg else None,
                'disqualification_reason': reg.disqualification_reason if reg else None,
                'registration_id': reg.id if reg else None,
            })

        return Response({
            'round_id': round_obj.id,
            'round_name': round_obj.name,
            'passing_count': passing_count,
            'total_teams': len(result),
            'results': results_list,
        })
