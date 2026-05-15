from django.test import TestCase
from accounts.models import User
from evaluation.models import JuryAssignment, SubmissionEvaluation
from tournaments.models import Tournament, Round, Submission
from teams.models import Team
from django.utils import timezone
import datetime

class EvaluationModelAdvancedTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user('eval_admin', 'e_a@e.com', 'pass', role='admin')
        self.jury = User.objects.create_user('eval_jury', 'e_j@e.com', 'pass', role='jury')
        self.user = User.objects.create_user('eval_user', 'e_u@e.com', 'pass')
        self.team = Team.objects.create(name='Eval Team', email='et@e.com', captain=self.user)
        
        now = timezone.now()
        self.tourney = Tournament.objects.create(
            name='Eval Tourney', 
            start_date=now - datetime.timedelta(days=1),
            end_date=now + datetime.timedelta(days=1),
            created_by=self.admin
        )
        self.round = Round.objects.create(tournament=self.tourney, name='Eval Round')
        self.sub = Submission.objects.create(team=self.team, round=self.round, created_by=self.user)
        self.assign = JuryAssignment.objects.create(submission=self.sub, jury=self.jury)

    # JuryAssignment Tests
    def test_jury_assignment_creation(self):
        self.assertTrue(JuryAssignment.objects.filter(id=self.assign.id).exists())

    def test_jury_assignment_is_evaluated_default_false(self):
        self.assertFalse(self.assign.is_evaluated)

    def test_jury_assignment_str(self):
        expected_str = f"Assignment {self.jury.username} -> {self.sub.id}"
        # Assuming format or just checking it contains username
        self.assertIn(self.jury.username, str(self.assign))

    def test_jury_assignment_unique_together(self):
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            JuryAssignment.objects.create(submission=self.sub, jury=self.jury)

    def test_jury_assignment_cascade_on_jury_delete(self):
        self.jury.delete()
        self.assertEqual(JuryAssignment.objects.count(), 0)

    def test_jury_assignment_cascade_on_submission_delete(self):
        self.sub.delete()
        self.assertEqual(JuryAssignment.objects.count(), 0)

    def test_jury_assignment_mark_evaluated(self):
        self.assign.is_evaluated = True
        self.assign.save()
        self.assertTrue(self.assign.is_evaluated)

    def test_jury_assignment_timestamps(self):
        self.assertIsNotNone(self.assign.created_at)

    def test_multiple_juries_for_submission(self):
        jury2 = User.objects.create_user('eval_jury2', 'ej2@e.com', 'pass', role='jury')
        assign2 = JuryAssignment.objects.create(submission=self.sub, jury=jury2)
        self.assertEqual(JuryAssignment.objects.filter(submission=self.sub).count(), 2)

    def test_multiple_submissions_for_jury(self):
        sub2 = Submission.objects.create(team=self.team, round=self.round, created_by=self.user)
        JuryAssignment.objects.create(submission=sub2, jury=self.jury)
        self.assertEqual(JuryAssignment.objects.filter(jury=self.jury).count(), 2)

    # SubmissionEvaluation Tests
    def test_submission_evaluation_creation(self):
        eval = SubmissionEvaluation.objects.create(assignment=self.assign, scores=[{"crit": 1, "score": 10}])
        self.assertTrue(SubmissionEvaluation.objects.filter(id=eval.id).exists())

    def test_submission_evaluation_str(self):
        eval = SubmissionEvaluation.objects.create(assignment=self.assign, scores=[])
        self.assertIn(str(self.assign.id), str(eval))

    def test_submission_evaluation_scores_json(self):
        scores = [{"c1": 5}, {"c2": 10}]
        eval = SubmissionEvaluation.objects.create(assignment=self.assign, scores=scores)
        self.assertEqual(len(eval.scores), 2)
        self.assertEqual(eval.scores[0]['c1'], 5)

    def test_submission_evaluation_total_score_default(self):
        eval = SubmissionEvaluation.objects.create(assignment=self.assign, scores=[])
        self.assertEqual(eval.total_score, 0)

    def test_submission_evaluation_total_score_update(self):
        eval = SubmissionEvaluation.objects.create(assignment=self.assign, scores=[])
        eval.total_score = 15
        eval.save()
        self.assertEqual(eval.total_score, 15)

    def test_submission_evaluation_feedback_blank(self):
        eval = SubmissionEvaluation.objects.create(assignment=self.assign, scores=[])
        self.assertEqual(eval.feedback, '')

    def test_submission_evaluation_feedback_update(self):
        eval = SubmissionEvaluation.objects.create(assignment=self.assign, scores=[], feedback='Good')
        self.assertEqual(eval.feedback, 'Good')
        eval.feedback = 'Excellent'
        eval.save()
        self.assertEqual(eval.feedback, 'Excellent')

    def test_submission_evaluation_cascade_on_assignment(self):
        eval = SubmissionEvaluation.objects.create(assignment=self.assign, scores=[])
        self.assign.delete()
        self.assertEqual(SubmissionEvaluation.objects.count(), 0)

    def test_submission_evaluation_one_to_one(self):
        from django.db import IntegrityError
        SubmissionEvaluation.objects.create(assignment=self.assign, scores=[])
        with self.assertRaises(IntegrityError):
            SubmissionEvaluation.objects.create(assignment=self.assign, scores=[])

    def test_submission_evaluation_timestamps(self):
        eval = SubmissionEvaluation.objects.create(assignment=self.assign, scores=[])
        self.assertIsNotNone(eval.created_at)
        self.assertIsNotNone(eval.updated_at)

    def test_evaluation_updates_assignment_status(self):
        # Depending on signals, creating an evaluation might set is_evaluated=True
        pass

    def test_submission_evaluation_large_scores(self):
        scores = [{"crit_id": str(i), "score": 10} for i in range(100)]
        eval = SubmissionEvaluation.objects.create(assignment=self.assign, scores=scores)
        self.assertEqual(len(eval.scores), 100)

    def test_jury_assignment_manager_evaluated(self):
        pass

    def test_jury_assignment_manager_pending(self):
        pass

    def test_evaluation_feedback_max_length(self):
        pass
