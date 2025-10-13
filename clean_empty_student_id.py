import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'voting_project.settings')
django.setup()

from users.models import UserProfile

UserProfile.objects.filter(student_id='').delete()
print("Deleted user profiles with empty student_id.")
