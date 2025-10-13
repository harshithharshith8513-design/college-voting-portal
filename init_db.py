import os
import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "voting_project.settings")
django.setup()

from django.contrib.auth import get_user_model

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
