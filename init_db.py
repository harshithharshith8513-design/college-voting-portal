import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "voting_project.settings")
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile

ADMIN_USERNAME = 'admin123'
ADMIN_EMAIL = 'admin123@gmail.com'
ADMIN_PASSWORD = 'discover01'  # Use a secure password!

# Create admin user if not exists
if not User.objects.filter(username=ADMIN_USERNAME).exists():
    user = User.objects.create_superuser(ADMIN_USERNAME, ADMIN_EMAIL, ADMIN_PASSWORD)
    print(f"Superuser '{ADMIN_USERNAME}' created.")
else:
    user = User.objects.get(username=ADMIN_USERNAME)
    print(f"Superuser '{ADMIN_USERNAME}' already exists.")

# Create UserProfile if not exists
if not UserProfile.objects.filter(roll_number=ADMIN_USERNAME).exists():
    UserProfile.objects.create(
        user=user,
        roll_number=ADMIN_USERNAME,
        student_id="ADMIN001",
        college_email=ADMIN_EMAIL,
        department="Admin",
        year="Admin",
        username="Admin"
    )
    print(f"UserProfile for '{ADMIN_USERNAME}' created.")
else:
    print(f"UserProfile for '{ADMIN_USERNAME}' already exists.")
