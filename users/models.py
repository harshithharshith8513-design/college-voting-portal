from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator

class ValidCollegeID(models.Model):
    college_id = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.college_id

    class Meta:
        verbose_name = "Valid College ID"
        verbose_name_plural = "Valid College IDs"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll_number = models.CharField(
        max_length=20, 
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z0-9]+$',
                message='Roll number must contain only letters and numbers (alphanumeric characters only)'
            )
        ],
        help_text="Roll number must contain both letters and numbers"
    )
    student_id = models.CharField(max_length=20, unique=True)  # College ID
    college_email = models.EmailField(unique=True)
    department = models.CharField(max_length=100)
    year = models.CharField(max_length=15)  # Increased for "Semester X"
    phone = models.CharField(max_length=15, null=True, blank=True)
    username = models.CharField(max_length=100)  # Can be duplicate (full name)
    has_voted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.roll_number} - {self.username}"

    def clean(self):
        from django.core.exceptions import ValidationError
        import re
        
        # Validate roll number contains both letters and numbers
        if self.roll_number:
            has_letter = bool(re.search(r'[A-Za-z]', self.roll_number))
            has_digit = bool(re.search(r'[0-9]', self.roll_number))
            
            if not (has_letter and has_digit):
                raise ValidationError({
                    'roll_number': 'Roll number must contain both letters and numbers'
                })

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
