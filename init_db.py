import os
import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "voting_project.settings")
django.setup()

from django.contrib.auth import get_user_model
import os
import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "voting_project.settings")
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile

# Create admin user if it does not exist
ADMIN_USERNAME = 'admin123'
ADMIN_EMAIL = 'admin123@gmail.com'
ADMIN_PASSWORD = 'discover01'  # Use your strong password

if not User.objects.filter(username=ADMIN_USERNAME).exists():
    user = User.objects.create_superuser(ADMIN_USERNAME, ADMIN_EMAIL, ADMIN_PASSWORD)
    
    # Also create UserProfile for this admin
    UserProfile.objects.create(
        user=user,
        roll_number=ADMIN_USERNAME,
        student_id="ADMIN001",
        college_email=ADMIN_EMAIL,
        department="Admin",
        year="Admin",
        username="Admin"
    )
    
    print(f"Admin user '{ADMIN_USERNAME}' and profile created successfully.")
else:
    print(f"Admin user '{ADMIN_USERNAME}' already exists.")

User = get_user_model()

# Create admin user if it does not exist
ADMIN_USERNAME = 'admin123'
ADMIN_EMAIL = 'admin123@gmail.com'
ADMIN_PASSWORD = 'your_strong_password'  # Change before deploying in production!

if not User.objects.filter(username=ADMIN_USERNAME).exists():
    User.objects.create_superuser(ADMIN_USERNAME, ADMIN_EMAIL, ADMIN_PASSWORD)
    print(f"Admin user '{ADMIN_USERNAME}' has been created.")
else:
    print(f"Admin user '{ADMIN_USERNAME}' already exists.")
