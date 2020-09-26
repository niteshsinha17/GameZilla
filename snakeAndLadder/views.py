from django.shortcuts import render
from .models import SNL, SNLMessage, SNLPlayer
from django.contrib.auth.decorators import login_required
import json
# Create your views here.


@login_required
def game(request, game_id):
    context = {}
    user = request.user
    game = SNL.objects.get(game_id=game_id)
    players = SNLPlayer.objects.filter(game=game)

    try:
        player = players.get(player=user)
    except:
        return render(request, 'game/not_allowed.html')

    # state = {
    #     'me': user.username,
    #     'game_id': game_id,
    #     'left': player.left,
    #     'sent': False,
    # }

    players_json = [{'name': player.player.username, 'color': player.color, 'left': player.left,
                     'bottom': player.bottom, 'pos': player.position} for player in players]
    context['players'] = players
    context['player'] = player
    context['game'] = game
    context['players_json'] = json.dumps(players_json)
    context['room_id'] = json.dumps({'room_id': game_id})
    context['me'] = json.dumps({'me': user.username})

    return render(request, 'snakeAndLadder/game.html', context)
