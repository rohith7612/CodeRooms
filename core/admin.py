from django.contrib import admin
from .models import Problem, Room, Participant, Submission, UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'matches_played', 'wins')
    search_fields = ('user__username',)
    list_filter = ('rating',)

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'topic', 'created_at')
    list_filter = ('difficulty', 'topic', 'created_at')
    search_fields = ('title', 'description', 'topic')
    ordering = ('-created_at',)

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_id', 'host', 'problem', 'is_active', 'anti_cheat_enabled', 'created_at')
    list_filter = ('is_active', 'anti_cheat_enabled', 'created_at', 'topic', 'difficulty')
    search_fields = ('room_id', 'host__username')
    ordering = ('-created_at',)
    list_editable = ('anti_cheat_enabled',)

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'score', 'completed_test_cases', 'tab_switches', 'finished_at')
    list_filter = ('room__room_id', 'finished_at')
    search_fields = ('user__username', 'room__room_id')

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('participant', 'passed', 'execution_time', 'timestamp')
    list_filter = ('passed', 'timestamp')
    search_fields = ('participant__user__username', 'participant__room__room_id', 'code')
    readonly_fields = ('execution_time', 'participant', 'code', 'output_log')
