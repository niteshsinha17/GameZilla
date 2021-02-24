from django.core.management.base import BaseCommand
from gamezilla.settings import BASE_DIR
from game.models import Game
from django.core.files import File
import pathlib


class Command(BaseCommand):
    help = "Use for creating games"
    result = []
    path = str(pathlib.Path(__file__).parent.absolute())
    games = [
        {
            "name": "Snake And Ladder",
            "code": "SNL",
            "min_player": 2,
            "max_player": 4,
            "img": "snl.jpg",
        },
        {
            "name": "Tic Tac Toe",
            "code": "TAC",
            "min_player": 2,
            "max_player": 2,
            "img": "tac.png",
        },
    ]

    def handle(self, *args, **kwargs):
        for game in self.games:
            try:
                Game.objects.get(code=game["code"])
                self.result.append(game["name"] + " is already created")
            except:
                _game = Game(
                    game_name=game["name"],
                    code=game["code"],
                    min_player=game["min_player"],
                    max_player=game["max_player"],
                )
                _game.save()
                _game.img.save(
                    game["img"], File(open(self.path + "/" + game["img"], "rb"))
                )
                self.result.append(game["name"] + " created ")
        for msg in self.result:
            self.stdout.write(self.style.SUCCESS(msg))
