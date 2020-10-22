from django.shortcuts import render, redirect
from .models import SNL, SNLMessage, SNLPlayer
from django.contrib.auth.decorators import login_required
import json
from django.contrib import messages

# Create your views here.


@login_required
def game(request, game_id):
    context = {}
    user = request.user
    try:
        game = SNL.objects.get(game_id=game_id)
    except:
        messages.add_message(
            request, messages.INFO, 'Game do not exists')
        return redirect('home')
    players = game.players.all()
    try:
        player = players.get(player=user)
    except:
        messages.add_message(
            request, messages.INFO, 'You are not allowed')
        return redirect('home')

    if game.started and (player.leaved or not player.entered):
        messages.add_message(
            request, messages.INFO, 'Cant join, You already leaved')
        return redirect('home')

    players_json = [{'name': player.player.username,
                     'position': player.position} for player in players]
    context['players'] = players
    context['messages'] = game.message.all()
    context['player'] = player
    context['game'] = game
    context['players_json'] = json.dumps(players_json)
    context['room_id'] = json.dumps({'room_id': game_id})
    context['me'] = json.dumps(
        {'me': user.username})

    return render(request, 'snakeAndLadder/game.html', context)
