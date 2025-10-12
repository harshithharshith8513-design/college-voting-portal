from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from elections.admin_views import (
    admin_dashboard, manage_elections, election_results, 
    manage_users, export_election_results, toggle_election_status, 
    live_vote_data
)
from users.admin_views import manage_college_ids, add_college_id, delete_college_id, bulk_add_college_ids, export_college_ids

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Custom Admin Dashboard URLs
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin-elections/', manage_elections, name='manage_elections'),
    path('admin-election-results/<int:election_id>/', election_results, name='election_results'),
    path('admin-users/', manage_users, name='manage_users'),
    path('admin-export/<int:election_id>/', export_election_results, name='export_election_results'),
    path('admin-toggle-status/<int:election_id>/', toggle_election_status, name='toggle_election_status'),
    path('admin-live-data/<int:election_id>/', live_vote_data, name='live_vote_data'),
    
    # College ID Management URLs
    path('admin-college-ids/', manage_college_ids, name='manage_college_ids'),
    path('admin-add-college-id/', add_college_id, name='add_college_id'),
    path('admin-delete-college-id/<int:id>/', delete_college_id, name='delete_college_id'),
    path('admin-bulk-add-college-ids/', bulk_add_college_ids, name='bulk_add_college_ids'),
    path('admin-export-college-ids/', export_college_ids, name='export_college_ids'),
    
    # Regular App URLs
    path('', include('users.urls')),
    path('users/', include('users.urls')),
    path('elections/', include('elections.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
