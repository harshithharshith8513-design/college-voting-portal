from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from .models import Election, Position, Candidate, Vote
from users.models import UserProfile
import csv
from datetime import datetime
from .forms import ElectionForm, CandidateForm, PositionForm


@staff_member_required
def admin_dashboard(request):
    """Main admin dashboard with statistics and quick actions"""
    total_users = User.objects.count()
    total_elections = Election.objects.count()
    active_elections = Election.objects.filter(status='active').count()
    total_votes = Vote.objects.count()
    total_college_ids = UserProfile.objects.count()
    used_college_ids = UserProfile.objects.count()
    available_college_ids = 0
    recent_votes = Vote.objects.select_related('voter', 'candidate', 'position').order_by('-timestamp')[:10]
    recent_users = User.objects.select_related('userprofile').order_by('-date_joined')[:5]
    election_stats = Election.objects.annotate(
        vote_count=Count('position__candidate__vote'),
        candidate_count=Count('position__candidate', distinct=True),
        position_count=Count('position', distinct=True)
    ).order_by('-id')[:5]
    dept_stats = UserProfile.objects.values('department').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    context = {
        'total_users': total_users,
        'total_elections': total_elections,
        'active_elections': active_elections,
        'total_votes': total_votes,
        'total_college_ids': total_college_ids,
        'used_college_ids': used_college_ids,
        'available_college_ids': available_college_ids,
        'recent_votes': recent_votes,
        'recent_users': recent_users,
        'election_stats': election_stats,
        'dept_stats': dept_stats,
    }
    return render(request, 'admin/custom_dashboard.html', context)


@staff_member_required
def manage_elections(request):
    status_filter = request.GET.get('status', '')
    elections_query = Election.objects.all().order_by('-start_date')
    if status_filter:
        elections_query = elections_query.filter(status=status_filter)
    active_count = Election.objects.filter(status='active').count()
    upcoming_count = Election.objects.filter(status='upcoming').count()
    ended_count = Election.objects.filter(status='ended').count()
    total_count = Election.objects.count()
    paginator = Paginator(elections_query, 10)
    page_number = request.GET.get('page')
    elections = paginator.get_page(page_number)
    context = {
        'elections': elections,
        'active_count': active_count,
        'upcoming_count': upcoming_count,
        'ended_count': ended_count,
        'total_count': total_count,
        'status_filter': status_filter,
    }
    return render(request, 'admin/manage_elections.html', context)


@staff_member_required
def election_results(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    results = {}
    for position in election.position_set.all().order_by('name'):
        candidates = position.candidate_set.annotate(
            total_votes=Count('vote')
        ).order_by('-total_votes')
        total_position_votes = sum(c.total_votes for c in candidates)
        for candidate in candidates:
            if total_position_votes > 0:
                candidate.percentage = (candidate.total_votes / total_position_votes) * 100
            else:
                candidate.percentage = 0
        results[position] = {
            'candidates': candidates,
            'total_votes': total_position_votes
        }
    context = {
        'election': election,
        'results': results,
    }
    return render(request, 'admin/election_results.html', context)


@staff_member_required
def manage_users(request):
    search_query = request.GET.get('search', '')
    department_filter = request.GET.get('department', '')
    users_query = User.objects.select_related('userprofile').order_by('-date_joined')
    if search_query:
        users_query = users_query.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(userprofile__student_id__icontains=search_query) |
            Q(userprofile__roll_number__icontains=search_query)
        )
    if department_filter:
        users_query = users_query.filter(userprofile__department=department_filter)
    departments = UserProfile.objects.values_list('department', flat=True).distinct()
    paginator = Paginator(users_query, 20)
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    context = {
        'users': users,
        'departments': departments,
        'search_query': search_query,
        'department_filter': department_filter,
    }
    return render(request, 'admin/manage_users.html', context)


@staff_member_required
def export_election_results(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename=\"election_results_{election.id}.csv\"'
    writer = csv.writer(response)
    writer.writerow(['Position', 'Candidate', 'Student ID', 'Votes', 'Percentage'])
    for position in election.position_set.all().order_by('name'):
        candidates = position.candidate_set.annotate(
            total_votes=Count('vote')
        ).order_by('-total_votes')
        total_votes = sum(c.total_votes for c in candidates)
        for candidate in candidates:
            percentage = (candidate.total_votes / total_votes * 100) if total_votes > 0 else 0
            writer.writerow([
                position.name,
                candidate.name,
                candidate.student_id,
                candidate.total_votes,
                f'{percentage:.2f}%'
            ])
    return response


@staff_member_required
def toggle_election_status(request, election_id):
    if request.method == 'POST':
        election = get_object_or_404(Election, id=election_id)
        new_status = request.POST.get('status')
        if new_status in ['active', 'ended', 'upcoming']:
            election.status = new_status
            election.save()
            messages.success(request, f'Election status updated to {new_status}')
        else:
            messages.error(request, 'Invalid status')
    return redirect('manage_elections')


@staff_member_required
def live_vote_data(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    data = {}
    for position in election.position_set.all().order_by('name'):
        candidates_data = []
        for candidate in position.candidate_set.all().order_by('name'):
            vote_count = candidate.vote_set.count()
            candidates_data.append({
                'name': candidate.name,
                'votes': vote_count
            })
        data[position.name] = candidates_data
    return JsonResponse(data)


# ----------- ADMIN MANAGEMENT & CRUD -----------


@staff_member_required
def election_management(request):
    search_query = request.GET.get('search', '')
    elections = Election.objects.all().order_by('-start_date')
    if search_query:
        elections = elections.filter(title__icontains=search_query)
    paginator = Paginator(elections, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'elections/election_management.html', {
        'elections': page_obj,
        'search_query': search_query,
    })


@staff_member_required
def candidate_management(request):
    search_query = request.GET.get('search', '')
    candidates = Candidate.objects.all().order_by('-id')
    if search_query:
        candidates = candidates.filter(name__icontains=search_query)
    paginator = Paginator(candidates, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'elections/candidate_management.html', {
        'candidates': page_obj,
        'search_query': search_query,
    })


@staff_member_required
def position_management(request):
    search_query = request.GET.get('search', '')
    positions = Position.objects.all().order_by('-id')
    if search_query:
        positions = positions.filter(name__icontains=search_query)
    paginator = Paginator(positions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'elections/position_management.html', {
        'positions': page_obj,
        'search_query': search_query,
    })


# --- CRUD for ELECTION ---
@staff_member_required
def create_election(request):
    if request.method == 'POST':
        form = ElectionForm(request.POST)
        if form.is_valid():
            election = form.save(commit=False)
            election.created_by = request.user  # FIX: sets created_by field!
            election.save()
            return redirect('election_management')
    else:
        form = ElectionForm()
    return render(request, 'elections/election_form.html', {'form': form, 'title': 'Create Election'})


@staff_member_required
def edit_election(request, pk):
    election = get_object_or_404(Election, pk=pk)
    if request.method == 'POST':
        form = ElectionForm(request.POST, instance=election)
        if form.is_valid():
            form.save()
            return redirect('election_management')
    else:
        form = ElectionForm(instance=election)
    return render(request, 'elections/election_form.html', {'form': form, 'title': 'Edit Election'})


@staff_member_required
def delete_election(request, pk):
    election = get_object_or_404(Election, pk=pk)
    if request.method == 'POST':
        election.delete()
        return redirect('election_management')
    return render(request, 'elections/confirm_delete.html', {'object': election, 'type': 'Election'})


# --- CRUD for CANDIDATE ---
@staff_member_required
def create_candidate(request):
    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('candidate_management')
    else:
        form = CandidateForm()
    return render(request, 'elections/candidate_form.html', {'form': form, 'title': 'Create Candidate'})


@staff_member_required
def edit_candidate(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES, instance=candidate)
        if form.is_valid():
            form.save()
            return redirect('candidate_management')
    else:
        form = CandidateForm(instance=candidate)
    return render(request, 'elections/candidate_form.html', {'form': form, 'title': 'Edit Candidate'})


@staff_member_required
def delete_candidate(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    if request.method == 'POST':
        candidate.delete()
        return redirect('candidate_management')
    return render(request, 'elections/confirm_delete.html', {'object': candidate, 'type': 'Candidate'})


# --- CRUD for POSITION ---
@staff_member_required
def create_position(request):
    if request.method == 'POST':
        form = PositionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('position_management')
    else:
        form = PositionForm()
    return render(request, 'elections/position_form.html', {'form': form, 'title': 'Create Position'})


@staff_member_required
def edit_position(request, pk):
    position = get_object_or_404(Position, pk=pk)
    if request.method == 'POST':
        form = PositionForm(request.POST, instance=position)
        if form.is_valid():
            form.save()
            return redirect('position_management')
    else:
        form = PositionForm(instance=position)
    return render(request, 'elections/position_form.html', {'form': form, 'title': 'Edit Position'})


@staff_member_required
def delete_position(request, pk):
    position = get_object_or_404(Position, pk=pk)
    if request.method == 'POST':
        position.delete()
        return redirect('position_management')
    return render(request, 'elections/confirm_delete.html', {'object': position, 'type': 'Position'})


# ---- Bulk Upload and Export for Users ----
from django.contrib.auth import get_user_model

@staff_member_required
def bulk_upload_users(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        file = request.FILES['csv_file']
        decoded_file = file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
        User = get_user_model()
        for row in reader:
            User.objects.update_or_create(
                username=row['username'],
                defaults={
                    'first_name': row.get('first_name', ''),
                    'last_name': row.get('last_name', ''),
                    'email': row.get('email', ''),
                }
            )
        messages.success(request, "Bulk user upload complete.")
        return redirect('manage_users')
    return render(request, 'elections/bulk_upload_users.html')

@staff_member_required
def export_users(request):
    User = get_user_model()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=users.csv'
    writer = csv.writer(response)
    writer.writerow(['username', 'first_name', 'last_name', 'email'])
    for user in User.objects.all():
        writer.writerow([user.username, user.first_name, user.last_name, user.email])
    return response

# ---- Bulk Upload and Export for Elections ----
@staff_member_required
def bulk_upload_elections(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        file = request.FILES['csv_file']
        decoded_file = file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
        for row in reader:
            Election.objects.update_or_create(
                title=row['title'],
                defaults={
                    'description': row.get('description', ''),
                    'start_date': row['start_date'],
                    'end_date': row['end_date'],
                    'status': row['status'],
                }
            )
        messages.success(request, "Bulk elections upload complete.")
        return redirect('election_management')
    return render(request, 'elections/bulk_upload_elections.html')

@staff_member_required
def export_elections(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=elections.csv'
    writer = csv.writer(response)
    writer.writerow(['title','description','start_date','end_date','status'])
    for e in Election.objects.all():
        writer.writerow([e.title,e.description,e.start_date,e.end_date,e.status])
    return response

# ---- Bulk Upload and Export for Positions ----
@staff_member_required
def bulk_upload_positions(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        file = request.FILES['csv_file']
        decoded_file = file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
        for row in reader:
            election = Election.objects.get(title=row['election'])
            Position.objects.update_or_create(
                name=row['name'],
                election=election,
                defaults={
                    'max_candidates': row.get('max_candidates', 1)
                }
            )
        messages.success(request, "Bulk positions upload complete.")
        return redirect('position_management')
    return render(request, 'elections/bulk_upload_positions.html')

@staff_member_required
def export_positions(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=positions.csv'
    writer = csv.writer(response)
    writer.writerow(['name','election','max_candidates'])
    for p in Position.objects.select_related('election').all():
        writer.writerow([p.name,p.election.title,p.max_candidates])
    return response

# ---- Bulk Upload and Export for Candidates ----
@staff_member_required
def bulk_upload_candidates(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        file = request.FILES['csv_file']
        decoded_file = file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
        for row in reader:
            position = Position.objects.get(name=row['position'])
            Candidate.objects.update_or_create(
                student_id=row['student_id'],
                defaults={
                    'name': row['name'],
                    'position': position,
                    'manifesto': row.get('manifesto','')
                }
            )
        messages.success(request, "Bulk candidates upload complete.")
        return redirect('candidate_management')
    return render(request, 'elections/bulk_upload_candidates.html')

@staff_member_required
def export_candidates(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=candidates.csv'
    writer = csv.writer(response)
    writer.writerow(['name','student_id','position','manifesto'])
    for c in Candidate.objects.select_related('position').all():
        writer.writerow([c.name,c.student_id,c.position.name,c.manifesto])
    return response
