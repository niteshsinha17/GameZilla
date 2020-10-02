from django.shortcuts import render, redirect
from .models import SNL, SNLMessage, SNLPlayer
from django.contrib.auth.decorators import login_required
import json
# Create your views here.


@login_required
def game(request, game_id):
    context = {}
    user = request.user
    try:
        game = SNL.objects.get(game_id=game_id)
    except:
        return render(request, 'game/no_room.html')
    players = SNLPlayer.objects.filter(game=game)

    try:
        player = players.get(player=user)
    except:
        return render(request, 'game/not_allowed.html')

    if game.started and not player.entered:
        return redirect('home')

    players_json = [{'name': player.player.username,
                     'position': player.position} for player in players]
    context['players'] = players
    context['player'] = player
    context['game'] = game
    context['players_json'] = json.dumps(players_json)
    context['room_id'] = json.dumps({'room_id': game_id})
    context['me'] = json.dumps(
        {'me': user.username })

    return render(request, 'snakeAndLadder/game.html', context)
