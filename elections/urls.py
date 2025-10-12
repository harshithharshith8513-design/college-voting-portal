from django.urls import path
from . import views
from . import admin_views

urlpatterns = [
    # User-Facing Votes/Election Views (keep your existing ones)
    path('dashboard/', views.dashboard, name='dashboard'),
    path('election/<int:election_id>/', views.election_detail, name='election_detail'),
    path('vote/<int:position_id>/', views.vote_for_position, name='vote_position'),

    # ----------- New: ADMIN MANAGEMENT VIEWS -----------
    # Main management cards dashboard page (linked from admin main cards)
    path('manage-elections/', admin_views.election_management, name='election_management'),
    path('manage-candidates/', admin_views.candidate_management, name='candidate_management'),
    path('manage-positions/', admin_views.position_management, name='position_management'),

    # Election CRUD
    path('election/create/', admin_views.create_election, name='create_election'),
    path('election/<int:pk>/edit/', admin_views.edit_election, name='edit_election'),
    path('election/<int:pk>/delete/', admin_views.delete_election, name='delete_election'),

    # Candidate CRUD
    path('candidate/create/', admin_views.create_candidate, name='create_candidate'),
    path('candidate/<int:pk>/edit/', admin_views.edit_candidate, name='edit_candidate'),
    path('candidate/<int:pk>/delete/', admin_views.delete_candidate, name='delete_candidate'),

    # Position CRUD
    path('position/create/', admin_views.create_position, name='create_position'),
    path('position/<int:pk>/edit/', admin_views.edit_position, name='edit_position'),
    path('position/<int:pk>/delete/', admin_views.delete_position, name='delete_position'),

    # ----------------- BULK UPLOAD & EXPORT ROUTES -----------------
    # Users
    path('users/bulk_upload/', admin_views.bulk_upload_users, name='bulk_upload_users'),
    path('users/export/', admin_views.export_users, name='export_users'),

    # Elections
    path('elections/bulk_upload/', admin_views.bulk_upload_elections, name='bulk_upload_elections'),
    path('elections/export/', admin_views.export_elections, name='export_elections'),

    # Positions
    path('positions/bulk_upload/', admin_views.bulk_upload_positions, name='bulk_upload_positions'),
    path('positions/export/', admin_views.export_positions, name='export_positions'),

    # Candidates
    path('candidates/bulk_upload/', admin_views.bulk_upload_candidates, name='bulk_upload_candidates'),
    path('candidates/export/', admin_views.export_candidates, name='export_candidates'),
]
