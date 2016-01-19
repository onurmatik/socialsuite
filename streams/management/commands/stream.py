"""
Upstart configuration

/etc/init/stream.conf

description "twitter stream"
start on runlevel [2345]
stop on runlevel [06]

respawn

script
    cd /home/ubuntu/bullsbears/
    . env/bin/activate
    python manage.py stream > stream.log
end script
"""


from django.core.management.base import BaseCommand
from streams.models import Stream


class Command(BaseCommand):
    def handle(self, **options):
        Stream.objects.listen()
