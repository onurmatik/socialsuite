from django.core.management.base import NoArgsCommand
from profiles.models import Profile


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        Profile.objects.update_profiles()
