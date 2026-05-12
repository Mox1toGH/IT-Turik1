from django.contrib import admin

from .models import Event, Round, Submission, Tournament, TournamentTeamRegistration


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'status', 'start_date', 'end_date')
    list_filter = ('status',)
    search_fields = ('name',)


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = ('id', 'tournament', 'name', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'evaluation_criteria')
    search_fields = ('name', 'tournament__name')


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'team', 'round', 'github_url', 'updated_at')
    search_fields = ('team__name', 'round__name', 'github_url')


@admin.register(TournamentTeamRegistration)
class TournamentTeamRegistrationAdmin(admin.ModelAdmin):
    list_display = ('id', 'tournament', 'team', 'created_by', 'created_at')
    search_fields = ('tournament__name', 'team__name', 'created_by__username')



@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'tournament', 'title', 'start_datetime')
    list_filter = ('tournament',)
    search_fields = ('title', 'tournament__name')

