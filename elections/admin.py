from django.contrib import admin
from .models import Election, Position, Candidate, Vote

@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_date', 'end_date', 'status', 'created_by']
    list_filter = ['status', 'start_date', 'created_by']
    search_fields = ['title', 'description']
    date_hierarchy = 'start_date'
    readonly_fields = ['created_by']
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['name', 'election', 'max_candidates']
    list_filter = ['election']
    search_fields = ['name']

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['name', 'student_id', 'position', 'vote_count']
    list_filter = ['position__election', 'position']
    search_fields = ['name', 'student_id']
    readonly_fields = ['vote_count']

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['voter', 'candidate', 'position', 'timestamp']
    list_filter = ['timestamp', 'position', 'position__election']
    search_fields = ['voter__username', 'candidate__name']
    readonly_fields = ['voter', 'candidate', 'position', 'timestamp']
    
    def has_add_permission(self, request):
        return False  # Prevent manual vote creation
    
    def has_change_permission(self, request, obj=None):
        return False  # Prevent vote modification
