from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import TAC, TACMessage
import json
from django.contrib import messages
# Create your views here.


def game(request, game_id):
    context = {}
    user = request.user
    try:
        game = TAC.objects.get(game_id=game_id)
    except:
        messages.add_message(
            request, messages.INFO, 'Game do not exists')
        return redirect('home')
    if user != game.zero and user != game.cross:
        messages.add_message(
            request, messages.INFO, 'You are not allowed')
        return redirect('home')
    context['game'] = game
    context['messages'] = TACMessage.objects.filter(game=game)
    context['details'] = json.dumps(
        {
            'me': user.username,
            'is_zero': user == game.zero,
            'room_id': game_id,
            'board': game.board
        }
    )

    return render(request, 'ticTacToe/game.html', context)
