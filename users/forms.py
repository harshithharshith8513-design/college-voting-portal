from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class RegistrationForm(UserCreationForm):
    full_name = forms.CharField(max_length=100, required=True)
    phone = forms.CharField(max_length=15, required=False)
    email = forms.EmailField(required=True)
    student_id = forms.CharField(max_length=20, required=True)
    college_email = forms.EmailField(required=True)
    department = forms.CharField(max_length=100, required=True)
    year = forms.CharField(max_length=10, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'full_name', 'student_id', 'college_email', 'department', 'year', 'password1', 'password2']

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if phone and UserProfile.objects.filter(phone=phone).exists():
            raise forms.ValidationError("Phone number already registered!")
        return phone

    def clean_student_id(self):
        student_id = self.cleaned_data['student_id']
        if UserProfile.objects.filter(student_id=student_id).exists():
            raise forms.ValidationError("Student ID already registered!")
        return student_id
