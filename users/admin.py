from django.contrib import admin
from .models import UserProfile, ValidCollegeID

@admin.register(ValidCollegeID)
class ValidCollegeIDAdmin(admin.ModelAdmin):
    list_display = ('college_id', 'created_at')
    search_fields = ('college_id',)
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('college_id')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'department', 'year', 'has_voted', 'created_at')
    list_filter = ('department', 'year', 'has_voted', 'created_at')
    search_fields = ('user__username', 'student_id', 'college_email')
    readonly_fields = ('created_at',)
