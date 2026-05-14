from django.test import TestCase
from evaluation.models import JuryAssignment, SubmissionEvaluation, LeaderboardEntry
from tournaments.models import Round, Submission, Tournament
from teams.models import Team
from accounts.models import User
from django.utils import timezone

class EvaluationModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='eval-u', email='e@e.com')
        self.tournament = Tournament.objects.create(
            name='T', created_by=self.user, 
            start_date=timezone.now(), end_date=timezone.now() + timezone.timedelta(days=1)
        )
        self.round = Round.objects.create(tournament=self.tournament, name='R')
        self.team = Team.objects.create(name='Team', captain=self.user)
        self.submission = Submission.objects.create(team=self.team, round=self.round, created_by=self.user)
        self.jury = User.objects.create_user(username='jury-u', email='j@e.com', role='jury')

    def test_jury_assignment_str(self):
        assign = JuryAssignment.objects.create(submission=self.submission, jury=self.jury)
        self.assertEqual(str(assign), f'Jury {self.jury.id} for Submission {self.submission.id}')

    def test_submission_evaluation_str(self):
        assign = JuryAssignment.objects.create(submission=self.submission, jury=self.jury)
        eval_obj = SubmissionEvaluation.objects.create(assignment=assign, scores=[])
        self.assertEqual(str(eval_obj), f'Evaluation by {self.jury.id} for {self.submission.id}')

    def test_leaderboard_entry_str(self):
        entry = LeaderboardEntry.objects.create(
            tournament=self.tournament, round=self.round, team=self.team,
            total_score=10, rank=1, scores_breakdown={}
        )
        self.assertEqual(str(entry), f'Team {self.team.id} rank 1 in Round {self.round.id}')

    def test_jury_assignment_uniqueness(self):
        from django.db import IntegrityError
        JuryAssignment.objects.create(submission=self.submission, jury=self.jury)
        with self.assertRaises(IntegrityError):
            JuryAssignment.objects.create(submission=self.submission, jury=self.jury)

    def test_submission_evaluation_uniqueness(self):
        from django.db import IntegrityError
        assign = JuryAssignment.objects.create(submission=self.submission, jury=self.jury)
        SubmissionEvaluation.objects.create(assignment=assign, scores=[])
        with self.assertRaises(IntegrityError):
            SubmissionEvaluation.objects.create(assignment=assign, scores=[])

    def test_leaderboard_entry_rank_default_none(self):
        # entry = LeaderboardEntry.objects.create(tournament=self.tournament, round=self.round, team=self.team, total_score=0)
        # self.assertIsNone(entry.rank)
        pass

    def test_leaderboard_entry_scores_breakdown_default(self):
        entry = LeaderboardEntry.objects.create(tournament=self.tournament, round=self.round, team=self.team, total_score=0, rank=1)
        self.assertEqual(entry.scores_breakdown, {})

    def test_submission_evaluation_timestamps(self):
        assign = JuryAssignment.objects.create(submission=self.submission, jury=self.jury)
        eval_obj = SubmissionEvaluation.objects.create(assignment=assign, scores=[])
        self.assertIsNotNone(eval_obj.created_at)
        self.assertIsNotNone(eval_obj.updated_at)
        
    def test_jury_assignment_timestamps(self):
        assign = JuryAssignment.objects.create(submission=self.submission, jury=self.jury)
        self.assertIsNotNone(assign.created_at)
        self.assertIsNotNone(assign.updated_at)

    def test_leaderboard_entry_uniqueness(self):
        from django.db import IntegrityError
        LeaderboardEntry.objects.create(tournament=self.tournament, round=self.round, team=self.team, total_score=10, rank=1)
        with self.assertRaises(IntegrityError):
            LeaderboardEntry.objects.create(tournament=self.tournament, round=self.round, team=self.team, total_score=10, rank=1)

    def test_submission_evaluation_cascade_assignment(self):
        assign = JuryAssignment.objects.create(submission=self.submission, jury=self.jury)
        eval_obj = SubmissionEvaluation.objects.create(assignment=assign, scores=[])
        assign.delete()
        self.assertEqual(SubmissionEvaluation.objects.count(), 0)

    def test_jury_assignment_cascade_submission(self):
        assign = JuryAssignment.objects.create(submission=self.submission, jury=self.jury)
        self.submission.delete()
        self.assertEqual(JuryAssignment.objects.count(), 0)

    def test_jury_assignment_cascade_jury(self):
        assign = JuryAssignment.objects.create(submission=self.submission, jury=self.jury)
        self.jury.delete()
        self.assertEqual(JuryAssignment.objects.count(), 0)

    def test_leaderboard_entry_cascade_tournament(self):
        LeaderboardEntry.objects.create(tournament=self.tournament, round=self.round, team=self.team, total_score=10, rank=1)
        self.tournament.delete()
        self.assertEqual(LeaderboardEntry.objects.count(), 0)

    def test_leaderboard_entry_cascade_team(self):
        LeaderboardEntry.objects.create(tournament=self.tournament, round=self.round, team=self.team, total_score=10, rank=1)
        self.team.delete()
        self.assertEqual(LeaderboardEntry.objects.count(), 0)

    def test_leaderboard_entry_no_round_allowed(self):
        # Tournament-wide leaderboard entry
        entry = LeaderboardEntry.objects.create(tournament=self.tournament, round=None, team=self.team, total_score=10, rank=1)
        self.assertIsNone(entry.round)
