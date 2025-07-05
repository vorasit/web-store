from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import UserProfile

class Command(BaseCommand):
    help = 'Creates UserProfile for existing users who do not have one.'

    def handle(self, *args, **options):
        users_without_profile = User.objects.filter(userprofile__isnull=True)
        for user in users_without_profile:
            UserProfile.objects.create(user=user)
            self.stdout.write(self.style.SUCCESS(f'Created UserProfile for {user.username}'))
        
        if not users_without_profile.exists():
            self.stdout.write(self.style.SUCCESS('All existing users already have a UserProfile.'))