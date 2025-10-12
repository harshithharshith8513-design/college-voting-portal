from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Q
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from .models import UserProfile, ValidCollegeID
import csv


@staff_member_required
def manage_college_ids(request):
    """Manage College IDs with pagination and search"""
    search_query = request.GET.get('search', '')
    
    college_ids_query = ValidCollegeID.objects.all().order_by('-created_at')
    
    if search_query:
        college_ids_query = college_ids_query.filter(
            college_id__icontains=search_query
        )
    
    paginator = Paginator(college_ids_query, 20)
    page_number = request.GET.get('page')
    college_ids = paginator.get_page(page_number)
    
    used_ids = UserProfile.objects.values_list('student_id', flat=True)
    
    total_ids = ValidCollegeID.objects.count()
    used_ids_count = UserProfile.objects.filter(
        student_id__in=ValidCollegeID.objects.values_list('college_id', flat=True)
    ).count()
    unused_ids = total_ids - used_ids_count
    
    context = {
        'college_ids': college_ids,
        'search_query': search_query,
        'used_ids': used_ids,
        'total_ids': total_ids,
        'used_ids_count': used_ids_count,
        'unused_ids': unused_ids,
    }
    
    return render(request, 'admin/manage_college_ids.html', context)


@staff_member_required
def add_college_id(request):
    """Add a new College ID"""
    if request.method == 'POST':
        college_id = request.POST.get('college_id', '').strip()
        
        if college_id:
            college_id_obj, created = ValidCollegeID.objects.get_or_create(
                college_id=college_id
            )
            if created:
                messages.success(request, f'College ID "{college_id}" added successfully')
            else:
                messages.warning(request, f'College ID "{college_id}" already exists')
        else:
            messages.error(request, 'College ID cannot be empty')
    
    return redirect('manage_college_ids')


@staff_member_required
def delete_college_id(request, id):  # ✅ Fixed: Changed parameter name from 'college_id' to 'id'
    """Delete a College ID"""
    college_id_obj = get_object_or_404(ValidCollegeID, id=id)  # ✅ Fixed: Using 'id' parameter
    
    # Check if the college ID is currently in use
    if UserProfile.objects.filter(student_id=college_id_obj.college_id).exists():
        messages.error(request, 'Cannot delete College ID - it is currently in use')
    else:
        college_id_value = college_id_obj.college_id  # Store value before deletion
        college_id_obj.delete()
        messages.success(request, f'College ID "{college_id_value}" deleted successfully')
    
    return redirect('manage_college_ids')


@staff_member_required
def bulk_add_college_ids(request):
    """Bulk add College IDs from CSV file"""
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        
        if csv_file:
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'File must be a CSV file')
                return redirect('manage_college_ids')
            
            try:
                file_data = csv_file.read().decode('utf-8').splitlines()
                reader = csv.reader(file_data)
                
                added_count = 0
                duplicate_count = 0
                
                for row in reader:
                    if row:
                        college_id = row[0].strip()
                        if college_id:
                            college_id_obj, created = ValidCollegeID.objects.get_or_create(
                                college_id=college_id
                            )
                            if created:
                                added_count += 1
                            else:
                                duplicate_count += 1
                
                messages.success(request, f'Added {added_count} new College IDs')
                if duplicate_count > 0:
                    messages.info(request, f'Skipped {duplicate_count} duplicate College IDs')
                    
            except Exception as e:
                messages.error(request, f'Error processing CSV file: {str(e)}')
        else:
            messages.error(request, 'No file selected')
    
    return redirect('manage_college_ids')


@staff_member_required
def export_college_ids(request):
    """Export College IDs to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="college_ids.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['College ID', 'Status', 'Added On'])
    
    used_ids = set(UserProfile.objects.values_list('student_id', flat=True))
    
    for college_id in ValidCollegeID.objects.all().order_by('-created_at'):
        status = 'Used' if college_id.college_id in used_ids else 'Available'
        writer.writerow([
            college_id.college_id,
            status,
            college_id.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response
