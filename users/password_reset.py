from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
import uuid

# Simple token storage (use database or cache in production)
reset_tokens = {}

def forgot_password(request):
    if request.method == 'POST':
        roll_number = request.POST.get('roll_number')
        
        try:
            user = User.objects.get(username=roll_number)
            
            if not user.email:
                messages.error(request, 'No email address found for this roll number. Please contact admin.')
                return render(request, 'users/forgot_password.html')
            
            # Generate unique token
            token = str(uuid.uuid4())
            reset_tokens[token] = {
                'user_id': user.id,
                'roll_number': roll_number
            }
            
            # Create reset link
            reset_link = request.build_absolute_uri(
                reverse('reset_password', args=[token])
            )
            
            # Email content
            subject = 'Password Reset - Discover College Voting'
            html_message = f'''
            <html>
            <body>
                <h2 style="color: #4a8cff;">Password Reset Request</h2>
                <p>Hello <strong>{user.first_name or roll_number}</strong>,</p>
                <p>You have requested to reset your password for Discover College Voting System.</p>
                <p>Click the button below to reset your password:</p>
                <div style="text-align: center; margin: 20px 0;">
                    <a href="{reset_link}" 
                       style="background-color: #4a8cff; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 5px; font-weight: bold;">
                        Reset Password
                    </a>
                </div>
                <p>Or copy and paste this link in your browser:</p>
                <p><a href="{reset_link}">{reset_link}</a></p>
                <p>If you did not request this password reset, please ignore this email.</p>
                <hr>
                <p><small>Best regards,<br>Discover College Voting System</small></p>
            </body>
            </html>
            '''
            
            plain_message = f'''
            Password Reset Request
            
            Hello {user.first_name or roll_number},
            
            You have requested to reset your password for Discover College Voting System.
            
            Click this link to reset your password:
            {reset_link}
            
            If you did not request this password reset, please ignore this email.
            
            Best regards,
            Discover College Voting System
            '''
            
            try:
                # Send email
                send_mail(
                    subject,
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                    html_message=html_message,
                )
                
                messages.success(
                    request, 
                    f'Password reset link has been sent to your registered email address ({user.email}). Please check your inbox.'
                )
                
            except Exception as e:
                messages.error(
                    request, 
                    f'Failed to send email. Please try again later or contact admin. Error: {str(e)}'
                )
                # Remove the token since email failed
                if token in reset_tokens:
                    del reset_tokens[token]
                
        except User.DoesNotExist:
            messages.error(request, 'Roll number not found.')
    
    return render(request, 'users/forgot_password.html')

def reset_password(request, token):
    if token not in reset_tokens:
        messages.error(request, 'Invalid or expired reset link.')
        return redirect('login')
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'users/reset_password.html')
        
        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'users/reset_password.html')
        
        # Update password
        user_data = reset_tokens[token]
        user = User.objects.get(id=user_data['user_id'])
        user.password = make_password(new_password)
        user.save()
        
        # Remove used token
        del reset_tokens[token]
        
        # Send confirmation email
        try:
            send_mail(
                'Password Reset Successful - Discover College Voting',
                f'Hello {user.first_name or user.username},\n\nYour password has been successfully reset for Discover College Voting System.\n\nIf you did not make this change, please contact admin immediately.\n\nBest regards,\nDiscover College Voting System',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )
        except:
            pass  # Don't show error for confirmation email failure
        
        messages.success(request, 'Password reset successful! Please login with your new password.')
        return redirect('login')
    
    return render(request, 'users/reset_password.html')
