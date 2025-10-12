from django import forms
from .models import Election, Candidate, Position

class ElectionForm(forms.ModelForm):
    class Meta:
        model = Election
        fields = ['title', 'description', 'start_date', 'end_date', 'status']

class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['name', 'election', 'max_candidates']

class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['name', 'student_id', 'position', 'manifesto', 'photo']
