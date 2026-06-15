from django.contrib import admin

from .models import JuryAssignment, LeaderboardEntry, SubmissionEvaluation


@admin.register(JuryAssignment)
class JuryAssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'submission', 'jury', 'get_round', 'created_at')
    list_filter = ('created_at', 'submission__round')
    search_fields = (
        'submission__team__name',
        'submission__round__name',
        'jury__username',
        'jury__email',
    )
    raw_id_fields = ('submission', 'jury')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

    def get_round(self, obj):
        return obj.submission.round

    get_round.short_description = 'Round'


@admin.register(SubmissionEvaluation)
class SubmissionEvaluationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'assignment',
        'get_submission',
        'get_jury',
        'total_score',
        'final_score',
        'created_at',
    )
    list_filter = ('created_at', 'assignment__submission__round')
    search_fields = (
        'assignment__submission__team__name',
        'assignment__submission__round__name',
        'assignment__jury__username',
        'assignment__jury__email',
    )
    raw_id_fields = ('assignment',)
    readonly_fields = ('total_score', 'final_score', 'created_at')
    date_hierarchy = 'created_at'

    def get_submission(self, obj):
        return obj.assignment.submission

    get_submission.short_description = 'Submission'

    def get_jury(self, obj):
        return obj.assignment.jury

    get_jury.short_description = 'Jury'


@admin.register(LeaderboardEntry)
class LeaderboardEntryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'tournament',
        'round',
        'team',
        'rank',
        'total_score',
        'average_score',
        'snapshot_at',
    )
    list_filter = ('tournament', 'round', 'snapshot_at')
    search_fields = ('tournament__name', 'round__name', 'team__name')
    raw_id_fields = ('tournament', 'round', 'team')
    readonly_fields = ('snapshot_at',)
    date_hierarchy = 'snapshot_at'
