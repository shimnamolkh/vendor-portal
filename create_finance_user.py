import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vendor_portal.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
username = 'finance1'
password = 'finance123'
email = 'finance1@aladrak.com'

try:
    if User.objects.filter(username=username).exists():
        print(f"User '{username}' already exists. Updating password...")
        user = User.objects.get(username=username)
        user.set_password(password)
        user.user_type = 'finance'
        user.is_staff = True
        user.is_superuser = False # NOT an admin
        user.save()
    else:
        print(f"Creating new user '{username}'...")
        user = User.objects.create_user(username=username, email=email, password=password)
        user.user_type = 'finance'
        user.is_staff = True
        user.is_superuser = False
        user.save()
    print(f"Successfully configured user: {username}")

except Exception as e:
    print(f"Error: {e}")
