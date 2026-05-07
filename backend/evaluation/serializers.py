from rest_framework import serializers
from accounts.models import User
from tournaments.models import Submission
from .models import JuryAssignment, SubmissionEvaluation
from tournaments.serializers import SubmissionSerializer
from tournaments.models import Tournament


class JuryAssignmentItemSerializer(serializers.Serializer):
    submission = serializers.PrimaryKeyRelatedField(queryset=Submission.objects.all())
    jury = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
    )

    def validate_jury(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError('Duplicate jury user ids are not allowed for a submission.')
        return value


class SubmissionEvaluationSerializer(serializers.ModelSerializer):
    tournament_id = serializers.PrimaryKeyRelatedField(
        source='tournament',
        queryset=Tournament.objects.all(),
        write_only=True,
        required=True,
    )

    class Meta:
        model = SubmissionEvaluation
        fields = (
            'id',
            'tournament_id',
            'assignment',
            'scores',
            'total_score',
            'final_score',
            'comment',
            'created_at',
        )
        read_only_fields = ('total_score', 'final_score', 'created_at')

    def validate_assignment(self, value):
        request = self.context.get('request')
        if value.jury_id != request.user.id:
            raise serializers.ValidationError('You are not assigned to this submission.')

        qs = SubmissionEvaluation.objects.filter(assignment=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError('This submission is already evaluated.')
        return value

    def validate(self, attrs):
        assignment = attrs.get('assignment')
        if not assignment and self.instance:
            assignment = self.instance.assignment
        tournament = attrs.pop('tournament', None)

        if assignment and tournament and assignment.submission.round.tournament_id != tournament.id:
            raise serializers.ValidationError(
                {'tournament_id': 'Assignment does not belong to this tournament.'}
            )

        scores = attrs.get('scores')

        if scores is not None and assignment:
            round_obj = assignment.submission.round
            criteria = round_obj.criteria
            
            if not criteria:
                raise serializers.ValidationError({"scores": "Round has no evaluation criteria."})
            
            criteria_dict = {c['id']: c for c in criteria}
            score_ids = set()
            
            for s in scores:
                c_id = s.get('criterion_id')
                if not c_id:
                     raise serializers.ValidationError({"scores": "Each score must have a criterion_id."})
                if c_id not in criteria_dict:
                     raise serializers.ValidationError({"scores": f"Invalid criterion_id: {c_id}"})
                if c_id in score_ids:
                     raise serializers.ValidationError({"scores": f"Duplicate criterion_id: {c_id}"})
                     
                score = s.get('score')
                if score is None or not isinstance(score, (int, float)) or score < 0 or score > criteria_dict[c_id]['max_score']:
                     raise serializers.ValidationError({"scores": f"Invalid score for {c_id}. Must be between 0 and {criteria_dict[c_id]['max_score']}"})
                score_ids.add(c_id)
                
            missing = set(criteria_dict.keys()) - score_ids
            if missing:
                raise serializers.ValidationError({"scores": f"Missing scores for criteria: {', '.join(missing)}"})

        return attrs


class JuryAssignmentSerializer(serializers.ModelSerializer):
    submission_details = SubmissionSerializer(source='submission', read_only=True)
    evaluation = SubmissionEvaluationSerializer(read_only=True)
    is_evaluated = serializers.SerializerMethodField()

    class Meta:
        model = JuryAssignment
        fields = ('id', 'submission', 'submission_details', 'evaluation', 'is_evaluated', 'created_at')

    def get_is_evaluated(self, obj):
        return hasattr(obj, 'evaluation')


class AvailableJurySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'full_name')
