from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from evaluation.models import JuryAssignment
from evaluation.leaderboard_service import (
    compute_leaderboard,
    compute_tournament_leaderboard,
    save_leaderboard_snapshot,
)
from evaluation.models import LeaderboardEntry, SubmissionEvaluation
from teams.models import Team
from tournaments.models import Round, Submission, Tournament
from tournaments.services import mark_round_evaluated


class ManualJuryAssignmentApiTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin_eval',
            email='admin_eval@example.com',
            password='TestPass123!',
            role='admin',
        )
        self.non_admin = User.objects.create_user(
            username='team_eval',
            email='team_eval@example.com',
            password='TestPass123!',
            role='team',
        )
        self.jury1 = User.objects.create_user(
            username='jury1_eval',
            email='jury1_eval@example.com',
            password='TestPass123!',
            role='jury',
        )
        self.jury2 = User.objects.create_user(
            username='jury2_eval',
            email='jury2_eval@example.com',
            password='TestPass123!',
            role='jury',
        )
        self.jury3 = User.objects.create_user(
            username='jury3_eval',
            email='jury3_eval@example.com',
            password='TestPass123!',
            role='jury',
        )

        self.organizer = User.objects.create_user(
            username='organizer_eval',
            email='organizer_eval@example.com',
            password='TestPass123!',
            role='organizer',
        )
        captain = User.objects.create_user(
            username='captain_eval',
            email='captain_eval@example.com',
            password='TestPass123!',
            role='team',
        )

        now = timezone.now()
        tournament = Tournament.objects.create(
            name='Eval Tournament',
            description='desc',
            start_date=now - timedelta(days=2),
            end_date=now + timedelta(days=2),
            status=Tournament.STATUS_RUNNING,
            created_by=self.organizer,
        )

        self.round_obj = Round.objects.create(
            tournament=tournament,
            name='Round 1',
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(hours=12),
            status=Round.STATUS_SUBMISSION_CLOSED,
            criteria=[{'id': 'backend', 'name': 'Backend', 'max_score': 10}],
        )

        self.team = Team.objects.create(
            name='Team Eval',
            email='team@example.com',
            captain=captain,
            is_public=True,
        )
        captain2 = User.objects.create_user(
            username='captain_eval_2',
            email='captain_eval_2@example.com',
            password='TestPass123!',
            role='team',
        )
        self.team2 = Team.objects.create(
            name='Team Eval 2',
            email='team2@example.com',
            captain=captain2,
            is_public=True,
        )
        self.submission1 = Submission.objects.create(
            team=self.team,
            round=self.round_obj,
            github_url='https://github.com/example/repo1',
            demo_video_url='https://youtu.be/demo1',
            created_by=captain,
        )
        self.submission2 = Submission.objects.create(
            team=self.team2,
            round=self.round_obj,
            github_url='https://github.com/example/repo2',
            demo_video_url='https://youtu.be/demo2',
            created_by=captain2,
        )

    def test_assign_jury_plain_array_replaces_existing_assignments(self):
        JuryAssignment.objects.create(submission=self.submission1, jury=self.jury3)

        payload = [
            {'submission': self.submission1.id, 'jury': [self.jury1.id, self.jury2.id]},
            {'submission': self.submission2.id, 'jury': [self.jury1.id, self.jury2.id]},
        ]

        self.client.force_authenticate(self.admin)
        response = self.client.post(
            reverse('round_assign_jury', kwargs={'pk': self.round_obj.id}),
            payload,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['created_assignments'], 4)
        pairs = set(
            JuryAssignment.objects.filter(submission__round=self.round_obj).values_list('submission_id', 'jury_id')
        )
        self.assertEqual(
            pairs,
            {
                (self.submission1.id, self.jury1.id),
                (self.submission1.id, self.jury2.id),
                (self.submission2.id, self.jury1.id),
                (self.submission2.id, self.jury2.id),
            },
        )

    def test_assign_jury_requires_full_submission_coverage(self):
        payload = [{'submission': self.submission1.id, 'jury': [self.jury1.id]}]
        self.client.force_authenticate(self.admin)
        response = self.client.post(reverse('round_assign_jury', kwargs={'pk': self.round_obj.id}), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('submission', response.data.get('details', {}))

    def test_assign_jury_requires_same_jury_count_per_submission(self):
        payload = [
            {'submission': self.submission1.id, 'jury': [self.jury1.id]},
            {'submission': self.submission2.id, 'jury': [self.jury1.id, self.jury2.id]},
        ]
        self.client.force_authenticate(self.admin)
        response = self.client.post(reverse('round_assign_jury', kwargs={'pk': self.round_obj.id}), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('jury', response.data.get('details', {}))

    def test_assign_jury_rejects_non_jury_user(self):
        payload = [
            {'submission': self.submission1.id, 'jury': [self.non_admin.id]},
            {'submission': self.submission2.id, 'jury': [self.non_admin.id]},
        ]
        self.client.force_authenticate(self.admin)
        response = self.client.post(reverse('round_assign_jury', kwargs={'pk': self.round_obj.id}), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('jury', response.data.get('details', {}))

    def test_assign_jury_rejects_when_round_not_submission_closed(self):
        self.round_obj.status = Round.STATUS_ACTIVE
        self.round_obj.save(update_fields=['status', 'updated_at'])
        payload = [
            {'submission': self.submission1.id, 'jury': [self.jury1.id]},
            {'submission': self.submission2.id, 'jury': [self.jury1.id]},
        ]
        self.client.force_authenticate(self.admin)
        response = self.client.post(reverse('round_assign_jury', kwargs={'pk': self.round_obj.id}), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_assign_jury_admin_only(self):
        payload = [
            {'submission': self.submission1.id, 'jury': [self.jury1.id]},
            {'submission': self.submission2.id, 'jury': [self.jury1.id]},
        ]
        self.client.force_authenticate(self.non_admin)
        response = self.client.post(reverse('round_assign_jury', kwargs={'pk': self.round_obj.id}), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_organizer_and_jury_can_assign_jury(self):
        for user in (self.organizer, self.jury1):
            with self.subTest(role=user.role):
                payload = [
                    {'submission': self.submission1.id, 'jury': [self.jury2.id]},
                    {'submission': self.submission2.id, 'jury': [self.jury2.id]},
                ]
                self.client.force_authenticate(user)
                response = self.client.post(
                    reverse('round_assign_jury', kwargs={'pk': self.round_obj.id}),
                    payload,
                    format='json',
                )
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_available_jury_returns_all_by_default(self):
        JuryAssignment.objects.create(submission=self.submission1, jury=self.jury1)
        self.client.force_authenticate(self.admin)
        response = self.client.get(reverse('round_available_jury', kwargs={'pk': self.round_obj.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = {item['id'] for item in response.data}
        self.assertEqual(returned_ids, {self.jury1.id, self.jury2.id, self.jury3.id})

    def test_available_jury_excludes_assigned_when_include_assigned_false(self):
        JuryAssignment.objects.create(submission=self.submission1, jury=self.jury1)
        self.client.force_authenticate(self.admin)
        response = self.client.get(
            reverse('round_available_jury', kwargs={'pk': self.round_obj.id}),
            {'include_assigned': 'false'},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = {item['id'] for item in response.data}
        self.assertEqual(returned_ids, {self.jury2.id, self.jury3.id})

    def test_available_jury_admin_only(self):
        self.client.force_authenticate(self.non_admin)
        response = self.client.get(reverse('round_available_jury', kwargs={'pk': self.round_obj.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class LeaderboardTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user('admin_lb', 'admin_lb@example.com', 'TestPass123!', role='admin')
        self.organizer = User.objects.create_user(
            'organizer_lb', 'organizer_lb@example.com', 'TestPass123!', role='organizer'
        )
        self.jury1 = User.objects.create_user('jury1_lb', 'jury1_lb@example.com', 'TestPass123!', role='jury')
        self.jury2 = User.objects.create_user('jury2_lb', 'jury2_lb@example.com', 'TestPass123!', role='jury')
        self.team_user = User.objects.create_user('team_lb', 'team_lb@example.com', 'TestPass123!', role='team')
        self.team_user2 = User.objects.create_user('team_lb2', 'team_lb2@example.com', 'TestPass123!', role='team')

        now = timezone.now()
        self.tournament = Tournament.objects.create(
            name='LB Tournament',
            description='desc',
            start_date=now - timedelta(days=2),
            end_date=now + timedelta(days=2),
            status=Tournament.STATUS_RUNNING,
            created_by=self.organizer,
        )
        self.round_obj = Round.objects.create(
            tournament=self.tournament,
            name='Qualifying',
            start_date=now - timedelta(days=2),
            end_date=now - timedelta(days=1),
            status=Round.STATUS_SUBMISSION_CLOSED,
            criteria=[
                {'id': 'innovation', 'name': 'Innovation', 'max_score': 10},
                {'id': 'design', 'name': 'Design', 'max_score': 10},
            ],
        )
        self.round_obj2 = Round.objects.create(
            tournament=self.tournament,
            name='Final',
            start_date=now - timedelta(hours=20),
            end_date=now + timedelta(hours=4),
            status=Round.STATUS_SUBMISSION_CLOSED,
            criteria=[
                {'id': 'innovation', 'name': 'Innovation', 'max_score': 10},
                {'id': 'design', 'name': 'Design', 'max_score': 10},
            ],
        )

        self.team1 = Team.objects.create(name='Team Alpha', email='alpha@example.com', captain=self.team_user, is_public=True)
        self.team2 = Team.objects.create(name='Team Beta', email='beta@example.com', captain=self.team_user2, is_public=True)

        self.sub1 = Submission.objects.create(
            team=self.team1,
            round=self.round_obj,
            github_url='https://github.com/example/a',
            demo_video_url='https://youtu.be/a',
            created_by=self.team_user,
        )
        self.sub2 = Submission.objects.create(
            team=self.team2,
            round=self.round_obj,
            github_url='https://github.com/example/b',
            demo_video_url='https://youtu.be/b',
            created_by=self.team_user2,
        )
        self.sub1_r2 = Submission.objects.create(
            team=self.team1,
            round=self.round_obj2,
            github_url='https://github.com/example/a-r2',
            demo_video_url='https://youtu.be/a-r2',
            created_by=self.team_user,
        )

        self.assign11 = JuryAssignment.objects.create(submission=self.sub1, jury=self.jury1)
        self.assign12 = JuryAssignment.objects.create(submission=self.sub1, jury=self.jury2)
        self.assign21 = JuryAssignment.objects.create(submission=self.sub2, jury=self.jury1)
        self.assign22 = JuryAssignment.objects.create(submission=self.sub2, jury=self.jury2)
        self.assign31 = JuryAssignment.objects.create(submission=self.sub1_r2, jury=self.jury1)
        self.assign32 = JuryAssignment.objects.create(submission=self.sub1_r2, jury=self.jury2)

        SubmissionEvaluation.objects.create(
            assignment=self.assign11,
            scores=[
                {'criterion_id': 'innovation', 'criterion_name': 'Innovation', 'score': 9},
                {'criterion_id': 'design', 'criterion_name': 'Design', 'score': 8},
            ],
        )
        SubmissionEvaluation.objects.create(
            assignment=self.assign12,
            scores=[
                {'criterion_id': 'innovation', 'criterion_name': 'Innovation', 'score': 8},
                {'criterion_id': 'design', 'criterion_name': 'Design', 'score': 8},
            ],
        )
        SubmissionEvaluation.objects.create(
            assignment=self.assign21,
            scores=[
                {'criterion_id': 'innovation', 'criterion_name': 'Innovation', 'score': 7},
                {'criterion_id': 'design', 'criterion_name': 'Design', 'score': 7},
            ],
        )
        SubmissionEvaluation.objects.create(
            assignment=self.assign22,
            scores=[
                {'criterion_id': 'innovation', 'criterion_name': 'Innovation', 'score': 6},
                {'criterion_id': 'design', 'criterion_name': 'Design', 'score': 7},
            ],
        )
        SubmissionEvaluation.objects.create(
            assignment=self.assign31,
            scores=[
                {'criterion_id': 'innovation', 'criterion_name': 'Innovation', 'score': 10},
                {'criterion_id': 'design', 'criterion_name': 'Design', 'score': 9},
            ],
        )
        SubmissionEvaluation.objects.create(
            assignment=self.assign32,
            scores=[
                {'criterion_id': 'innovation', 'criterion_name': 'Innovation', 'score': 9},
                {'criterion_id': 'design', 'criterion_name': 'Design', 'score': 9},
            ],
        )

    def test_compute_leaderboard_returns_correct_rank_order(self):
        self.round_obj.status = Round.STATUS_EVALUATED
        self.round_obj.save(update_fields=['status', 'updated_at'])
        rankings = compute_leaderboard(self.round_obj.id)
        self.assertEqual(rankings[0]['team_id'], self.team1.id)
        self.assertEqual(rankings[0]['rank'], 1)
        self.assertEqual(rankings[1]['team_id'], self.team2.id)
        self.assertEqual(rankings[1]['rank'], 2)

    def test_save_leaderboard_snapshot_is_idempotent(self):
        save_leaderboard_snapshot(self.tournament.id, self.round_obj.id)
        save_leaderboard_snapshot(self.tournament.id, self.round_obj.id)
        self.assertEqual(
            LeaderboardEntry.objects.filter(tournament=self.tournament, round=self.round_obj).count(),
            2,
        )

    def test_compute_tournament_leaderboard_sums_only_participated_rounds(self):
        rankings = compute_tournament_leaderboard(self.tournament.id)
        team1_row = next(row for row in rankings if row['team_id'] == self.team1.id)
        team2_row = next(row for row in rankings if row['team_id'] == self.team2.id)

        self.assertEqual(len(team1_row['rounds']), 2)
        self.assertEqual(len(team2_row['rounds']), 1)
        summed = sum(round_row['total_score'] for round_row in team1_row['rounds'])
        self.assertEqual(team1_row['total_score'], summed)
        self.assertGreater(team1_row['total_score'], team2_row['total_score'])
        self.assertEqual(rankings[0]['team_id'], self.team1.id)

    def test_team_role_sees_jury_breakdown_null(self):
        self.round_obj.status = Round.STATUS_EVALUATED
        self.round_obj2.status = Round.STATUS_EVALUATED
        self.round_obj.save(update_fields=['status', 'updated_at'])
        self.round_obj2.save(update_fields=['status', 'updated_at'])
        self.client.force_authenticate(self.team_user)
        response = self.client.get(reverse('tournament_leaderboard', kwargs={'tournament_id': self.tournament.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for round_row in response.data['rankings'][0]['rounds']:
            self.assertIsNone(round_row['jury_breakdown'])

    def test_admin_organizer_jury_see_jury_breakdown(self):
        self.round_obj.status = Round.STATUS_EVALUATED
        self.round_obj2.status = Round.STATUS_EVALUATED
        self.round_obj.save(update_fields=['status', 'updated_at'])
        self.round_obj2.save(update_fields=['status', 'updated_at'])
        for user in (self.admin, self.organizer, self.jury1):
            with self.subTest(role=user.role):
                self.client.force_authenticate(user)
                response = self.client.get(
                    reverse('tournament_leaderboard', kwargs={'tournament_id': self.tournament.id})
                )
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertIsNotNone(response.data['rankings'][0]['rounds'][0]['jury_breakdown'])

    def test_live_endpoint_returns_403_for_team_if_round_not_evaluated(self):
        self.round_obj.status = Round.STATUS_ACTIVE
        self.round_obj.save(update_fields=['status', 'updated_at'])
        self.client.force_authenticate(self.team_user)
        response = self.client.get(reverse('round_leaderboard', kwargs={'round_id': self.round_obj.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_archived_endpoint_reads_from_snapshot_not_live_evaluations(self):
        self.round_obj.status = Round.STATUS_EVALUATED
        self.round_obj2.status = Round.STATUS_EVALUATED
        self.round_obj.save(update_fields=['status', 'updated_at'])
        self.round_obj2.save(update_fields=['status', 'updated_at'])
        save_leaderboard_snapshot(self.tournament.id, self.round_obj.id)
        save_leaderboard_snapshot(self.tournament.id, self.round_obj2.id)
        self.tournament.status = Tournament.STATUS_FINISHED
        self.tournament.save(update_fields=['status', 'updated_at'])

        eval_obj = SubmissionEvaluation.objects.get(assignment=self.assign11)
        eval_obj.scores = [
            {'criterion_id': 'innovation', 'criterion_name': 'Innovation', 'score': 1},
            {'criterion_id': 'design', 'criterion_name': 'Design', 'score': 1},
        ]
        eval_obj.save()

        self.client.force_authenticate(self.admin)
        response = self.client.get(reverse('tournament_leaderboard', kwargs={'tournament_id': self.tournament.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_snapshot'])
        self.assertGreater(response.data['rankings'][0]['total_score'], 10)

    def test_snapshot_created_when_tournament_transitions_to_finished(self):
        self.round_obj.status = Round.STATUS_SUBMISSION_CLOSED
        self.round_obj2.status = Round.STATUS_SUBMISSION_CLOSED
        self.round_obj.save(update_fields=['status', 'updated_at'])
        self.round_obj2.save(update_fields=['status', 'updated_at'])
        mark_round_evaluated(self.round_obj)
        mark_round_evaluated(self.round_obj2)
        self.assertTrue(
            LeaderboardEntry.objects.filter(
                tournament=self.tournament,
                round__isnull=True,
                rounds_breakdown__isnull=False,
            ).exists()
        )
        self.assertEqual(
            LeaderboardEntry.objects.filter(tournament=self.tournament, round__isnull=True).count(),
            2,
        )

    def test_tournament_snapshot_idempotent(self):
        self.round_obj.status = Round.STATUS_SUBMISSION_CLOSED
        self.round_obj2.status = Round.STATUS_SUBMISSION_CLOSED
        self.round_obj.save(update_fields=['status', 'updated_at'])
        self.round_obj2.save(update_fields=['status', 'updated_at'])
        save_leaderboard_snapshot(self.tournament.id, self.round_obj2.id)
        first_count = LeaderboardEntry.objects.filter(tournament=self.tournament, round__isnull=True).count()
        save_leaderboard_snapshot(self.tournament.id, self.round_obj2.id)
        second_count = LeaderboardEntry.objects.filter(tournament=self.tournament, round__isnull=True).count()
        self.assertEqual(first_count, second_count)
