#!/usr/bin/env python
"""
Script untuk menjalankan database operations di Vercel environment
Bisa dijalankan dari Vercel dashboard via shell atau API endpoint
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'langlearn_config.settings')
sys.path.insert(0, str(Path(__file__).resolve().parent))

django.setup()

from django.core.management import call_command

def run_migrations():
    """Run database migrations"""
    print("🔄 Running database migrations...")
    try:
        call_command('migrate', '--run-syncdb')
        print("✅ Migrations completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def collect_static():
    """Collect static files"""
    print("📦 Collecting static files...")
    try:
        call_command('collectstatic', '--noinput')
        print("✅ Static files collected successfully!")
        return True
    except Exception as e:
        print(f"❌ Static collection failed: {e}")
        return False

def create_superuser():
    """Create default superuser if not exists"""
    print("👤 Checking superuser...")
    from django.contrib.auth.models import User
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@langlearn.com', 'change_me_in_admin')
        print("✅ Superuser 'admin' created!")
    else:
        print("ℹ️ Superuser 'admin' already exists")

if __name__ == '__main__':
    run_migrations()
    collect_static()
    create_superuser()
    print("\n✨ Setup complete!")
