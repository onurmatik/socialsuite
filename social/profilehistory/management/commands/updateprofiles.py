from django.core.management.base import NoArgsCommand
from social.users.models import ProfileHistory


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        ProfileHistory.objects.update_history()
