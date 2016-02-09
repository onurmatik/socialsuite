"""
Upstart configuration

/etc/init/stream.conf

description "twitter streamer"
start on runlevel [2345]
stop on runlevel [!2345]

respawn

script
    cd /home/ubuntu/[project]/
    . env/bin/activate
    python manage.py stream > stream.log
end script
"""


from django.core.management.base import BaseCommand
from social.streams.models import Stream


class Command(BaseCommand):
    def handle(self, **options):
        Stream.objects.listen()
