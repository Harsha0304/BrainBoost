#!/bin/sh

echo "📦 Applying migrations..."
python manage.py migrate --noinput

echo "👤 Ensuring admin user exists..."
python manage.py shell << END
from django.contrib.auth import get_user_model

User = get_user_model()

username = "admin"
password = "admin123"

user, created = User.objects.get_or_create(username=username)

if created:
    print("Creating admin user...")
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.save()
else:
    print("Admin user exists. Resetting password...")
    user.set_password(password)
    user.save()

print("Admin credentials ensured.")
END

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "🚀 Starting Django server..."
exec gunicorn brainboost_core.wsgi:application --bind 0.0.0.0:8000