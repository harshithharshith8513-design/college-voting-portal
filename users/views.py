from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import UserProfile, ValidCollegeID
import re

def register_view(request):
    if request.method == 'POST':
        # Get form data
        roll_number = request.POST.get('roll_number', '').strip()
        username = request.POST.get('username', '').strip()  # This is full name now
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        student_id = request.POST.get('student_id', '').strip()
        department = request.POST.get('department', '').strip()
        year = request.POST.get('year', '').strip()
        phone = request.POST.get('phone', '').strip()

        # Validation
        errors = []

        # Validate roll number (alphanumeric with both letters and numbers)
        if not roll_number:
            errors.append('Roll number is required')
        elif len(roll_number) < 4:
            errors.append('Roll number must be at least 4 characters long')
        elif not re.match(r'^[A-Za-z0-9]+$', roll_number):
            errors.append('Roll number must contain only letters and numbers')
        else:
            # Check if contains both letters and digits
            has_letter = bool(re.search(r'[A-Za-z]', roll_number))
            has_digit = bool(re.search(r'[0-9]', roll_number))
            if not (has_letter and has_digit):
                errors.append('Roll number must contain both letters and numbers')
            
            # Check if roll number is unique
            if User.objects.filter(username=roll_number).exists():
                errors.append('This roll number is already registered')

        # Validate other required fields
        if not username:
            errors.append('Full name is required')
        if not email:
            errors.append('Email is required')
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters long')
        if not student_id:
            errors.append('College ID is required')
        if not department:
            errors.append('Department is required')
        if not year:
            errors.append('Year/Semester is required')

        # Validate College ID exists in valid list
        if student_id and not ValidCollegeID.objects.filter(college_id=student_id).exists():
            errors.append('Invalid College ID. Please contact administrator.')

        # Check if College ID already used
        if student_id and UserProfile.objects.filter(student_id=student_id).exists():
            errors.append('This College ID is already registered')

        # Check if email already exists
        if email and User.objects.filter(email=email).exists():
            errors.append('This email is already registered')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'users/register.html')

        try:
            # Create User with roll_number as username
            user = User.objects.create_user(
                username=roll_number,  # Roll number is now the username
                email=email,
                password=password,
                first_name=username.split()[0] if username else '',
                last_name=' '.join(username.split()[1:]) if len(username.split()) > 1 else ''
            )

            # Update the UserProfile created by signals with proper data
            try:
                profile = UserProfile.objects.get(user=user)
                profile.roll_number = roll_number
                profile.username = username  # Full name stored here
                profile.student_id = student_id
                profile.college_email = email
                profile.department = department
                profile.year = year
                profile.phone = phone if phone else None
                profile.save()
            except UserProfile.DoesNotExist:
                # Create profile if signal didn't create it
                UserProfile.objects.create(
                    user=user,
                    roll_number=roll_number,
                    username=username,
                    student_id=student_id,
                    college_email=email,
                    department=department,
                    year=year,
                    phone=phone if phone else None
                )

            messages.success(request, 'Registration successful! Please login with your roll number.')
            return redirect('login')

        except Exception as e:
            # If user was created but profile failed, clean up
            try:
                user = User.objects.get(username=roll_number)
                user.delete()
            except:
                pass
            messages.error(request, f'Registration failed: {str(e)}')

    return render(request, 'users/register.html')

def login_view(request):
    if request.method == 'POST':
        roll_number = request.POST.get('username', '').strip()  # Field name is 'username' but contains roll number
        password = request.POST.get('password', '').strip()

        if not roll_number or not password:
            messages.error(request, 'Please enter both roll number and password')
            return render(request, 'users/login.html')

        # Validate roll number format before authentication
        if roll_number:
            has_letter = bool(re.search(r'[A-Za-z]', roll_number))
            has_digit = bool(re.search(r'[0-9]', roll_number))
            is_alphanumeric = bool(re.match(r'^[A-Za-z0-9]+$', roll_number))
            
            if not (is_alphanumeric and has_letter and has_digit):
                messages.error(request, 'Invalid roll number format')
                return render(request, 'users/login.html')

        user = authenticate(request, username=roll_number, password=password)
        if user:
            login(request, user)
            # Safe way to get username - check if profile exists
            try:
                welcome_name = user.userprofile.username or user.username
            except (UserProfile.DoesNotExist, AttributeError):
                welcome_name = user.username
            
            messages.success(request, f'Welcome back, {welcome_name}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid roll number or password')

    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('login')

# Additional utility function for safe profile access
def get_user_profile_safe(user):
    """Safely get user profile with fallback"""
    try:
        return user.userprofile
    except UserProfile.DoesNotExist:
        # Create empty profile if doesn't exist
        return UserProfile.objects.create(
            user=user,
            roll_number=user.username,
            username=f"{user.first_name} {user.last_name}".strip() or user.username,
            student_id='',
            college_email=user.email or '',
            department='',
            year=''
        )
