from django.core.management.base import NoArgsCommand
from users.models import Profile


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        Profile.objects.update_history()
