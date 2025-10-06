# users/management/commands/seed_users.py
from django.core.management.base import BaseCommand
from users.models import User, UserProfile

class Command(BaseCommand):
    help = 'Seed initial user data'
    
    def handle(self, *args, **options):
        # Create sample users
        users_data = [
            {'email': 'admin@wpsauto.com', 'phone_number': '13800138001', 'is_staff': True, 'is_superuser': True},
            {'email': 'user1@example.com', 'phone_number': '13800138002'},
            {'email': 'user2@example.com', 'phone_number': '13800138003'},
        ]
        
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults=user_data
            )
            if created:
                user.set_password('testpass123')
                user.save()
                UserProfile.objects.create(user=user)
                self.stdout.write(
                    self.style.SUCCESS(f'Created user: {user.email}')
                )