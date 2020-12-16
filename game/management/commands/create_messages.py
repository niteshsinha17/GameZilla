from django.core.management.base import BaseCommand
from gamezilla.settings import BASE_DIR
from game.models import RoomMessage
from django.core.files import File
import pathlib

HOST_MESSAGES = [
    {'msg': 'Lets start the game?'},
    {'msg': 'Lets change the game?'},
    {'msg': 'Everyone get ready!'},
    {'msg': 'Want to invite anyone?'},
    {'msg': 'Yes'},
    {'msg': 'No'},
]

MESSAGES = [
    {'msg': 'Wait a minute!'},
    {'msg': 'Change the game'},
    {'msg': 'Lets get started'},
    {'msg': 'Yes'},
    {'msg': 'No'},
]


class Command(BaseCommand):
    help = 'Used for creating room messages'

    def handle(self, *args, **kwargs):
        count = 0
        for message in HOST_MESSAGES:
            try:
                msg = RoomMessage(msg=message['msg'], host=True)
                msg.save()
                count += 1
            except:
                pass

        for message in MESSAGES:
            try:
                msg = RoomMessage(msg=message[msg], host=False)
                msg.save()
                count += 1
            except:
                pass

        self.stdout.write(self.style.SUCCESS(str(count) + ' messages created'))
