import time
from django.shortcuts import render, redirect
# from account.models import User
from django.contrib.auth.models import User
from game.models import Game, Room, Member
import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.contrib import messages
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Q
from snakeAndLadder.models import SNL
from ticTacToe.models import TAC

from .forms import ReportForm
# Create your views here.


@login_required
def home(request):
    user = request.user
    context = {}
    games = Game.objects.all()
    hosted_rooms = Room.objects.get_hosted_rooms(user=user)
    joined_romms = Member.objects.get_joined_rooms(user=user)
    context['games'] = games
    context['hosted_rooms'] = hosted_rooms
    context['joined_rooms'] = joined_romms
    return render(request, 'game/home.html', context)


@login_required
def host_game(request, game_code):
    user = request.user
    game = Game.objects.get(code=game_code)
    if not Room.objects.can_create_room(user=user):
        messages.add_message(
            request, messages.INFO, 'You have created maximum rooms. Please exit from there to create new room')
        return redirect('home')
    room = Room(game=game, created_by=user)
    room.max_members = game.max_player
    room.save()
    return redirect('host_room', sp_id=room.sp_id)


@login_required
def host_room_view(request, sp_id):
    context = {}
    user = request.user
    try:
        room = Room.objects.get(sp_id=sp_id)
    except:
        messages.add_message(
            request, messages.INFO, 'NO SUCH ROOM')
        return redirect('home')

    if room.created_by != user:
        return redirect('join', sp_id=room.sp_id)

    if room.started:
        member = Member.objects.filter(
            member=user, room=room)[0]
        if not member.leaved:
            return redirect(room.game_url)

    # game is not started
    # check host is created or not as a member
    created = True
    members = Member.objects.filter(room=room)
    try:
        member = members.get(member=user)
        member.online = True
        member.save()
    except:
        # entering first time
        created = False

    if not created:
        member = Member(member=user, host=True, ready=True)
        member.room = room
        member.save()
        room.members_joined += 1
        room.save()
    if room.started:
        # change memebers to show
        members = list(members.filter(leaved=False))
        members.append(member)

    state = room.get_state()
    state['me'] = user.username
    context['games'] = Game.objects.all()
    context['selected_game'] = room.game
    context['members'] = members
    context['state'] = json.dumps(state)
    context['room'] = room
    context['me'] = member
    return render(request, 'game/room.html', context)


@login_required
def report(request):
    if request.POST:
        report_form = ReportForm(request.user, request.POST)
        if report_form.is_valid():
            report_form.save()
            messages.add_message(
                request, messages.INFO, 'Thanks for reporting')
            return redirect('home')
    else:
        report_form = ReportForm(request.user)
    return render(request, 'game/report.html', {'report_form': report_form})


@login_required
def join_game(request, sp_id=None):
    context = {}
    user = request.user
    try:
        room = Room.objects.get(sp_id=sp_id)
    except:
        messages.add_message(
            request, messages.INFO, 'No such room')
        return redirect('home')
    members = Member.objects.filter(room=room)
    if (room.created_by == user):
        return redirect('host_room', sp_id=sp_id)

    # check member is already created or not
    created = True
    try:
        member = members.get(member=user)
        if member.leaved:
            messages.add_message(
                request, messages.INFO, 'You have leaved the room, Wait for the gave to over')
            return redirect('home')
        member.online = True
        member.save()
    except:
        created = False
        if room.started:
            messages.add_message(
                request, messages.INFO, 'Game has already started')
            return redirect('home')

    if created and room.started:
        return redirect(room.game_url)

    if not created:
        # check space is available or not
        if room.members_joined < room.max_members:
            # create a member
            member = Member(member=user, room=room)
            member.save()
            room.members_joined += 1
            room.save()
        else:
            # NO space available
            messages.add_message(
                request, messages.INFO, 'Room is Full')
            return redirect('home')

    state = room.get_state()
    state['me'] = user.username
    context['games'] = Game.objects.all()
    context['selected_game'] = room.game
    context['members'] = members
    context['state'] = json.dumps(state)
    context['me'] = member
    context['room'] = room
    return render(request, 'game/join_room.html', context)


@login_required
def join_room(request):
    # join room through form
    sp_id = request.POST.get('sp-id')
    return redirect('join', sp_id=sp_id)


@login_required
def leave(request, sp_id):
    try:
        room = Room.objects.get(sp_id=sp_id)
    except:
        return HttpResponse(json.dumps({
            'deleted': False,
            'reason': 'Room is already deleted'
        }))
    user = request.user
    try:
        member = Member.objects.filter(room=room).get(member=user)
    except:
        messages.add_message(
            request, messages.INFO, 'No such room')
        return redirect('home')
    if member.host:
        if room.started:
            '''
            delete room if condition is satisfied
            '''
            game_code = room.game.code
            if game_code == 'SNL':
                game = SNL.objects.get(game_id=sp_id)
                if game.players.filter(Q(online=False) | Q(disable=True) | Q(leaved=True)).count() == game.max_player:
                    room.delete()
                    return HttpResponse(json.dumps({
                        'deleted': True,
                        'reason': 'Room deleted!'
                    }))
            elif game_code == "TAC":
                game = TAC.objects.get(game_id=sp_id)
                if not game.zero_active and not game.cross_active:
                    room.delete()
                    return HttpResponse(json.dumps({
                        'deleted': True,
                        'reason': 'Room deleted!'
                    }))
            return HttpResponse(json.dumps({
                'deleted': False,
                'reason': 'other players playing. Please wait!'
            }))

        # room not started
        # delete it
        try:
            room.delete()
            msg = {
                'action': 'leaved',
                'member': 'all'
            }
            send_leave_msg(sp_id, msg)

        except:
            return HttpResponse(json.dumps({
                'delete': False,
                'reason': 'Try Again'
            }))

        return HttpResponse(json.dumps({
            'deleted': True,
            'reason': 'Room deleted!'
        }))
    else:
        if room.started:
            if room.game.code == "SNL":
                game = SNL.objects.get(room=room)
                room = game.room
                try:
                    player = game.players.get(player=user)
                except:
                    member.leaved = True
                    member.save()
                    return HttpResponse(json.dumps({
                        'deleted': True,
                        'reason': 'You leaved the game'
                    }))
                if player.leaved:
                    return HttpResponse(json.dumps({'deleted': False, 'reason': 'invalid player'}))
                room.members_joined -= 1
                room.members_ready -= 1
                room.save()
                if player.disable:
                    # only remove from room and game
                    player.leaved = True
                    player.save()
                    msg = {
                        'action': 'leaved',
                        'leaved_msg': user.username + ' leaved the game',
                        'start': False, 'member': user.username,
                        'was_ready': True
                    }
                    send_leave_msg(sp_id, msg)
                    return HttpResponse(json.dumps({'deleted': True, 'reason': 'you leaved the room'}))

                game.players_playing -= 1
                member = Member.objects.filter(room=room).get(member=user)
                member.leaved = True
                player.leaved = True
                member.save()
                player.save()
                if game.players_playing == 1:
                    # game over situation
                    game.winner_state += 1
                    player.rank = game.winner_state
                    player.save()
                    game.save()
                    winners = [{'name': player.player.username,
                                'rank': player.rank}
                               for player in game.players.all()
                               ]
                    room.reset()
                    game.delete()
                    msg = {
                        'action': 'game_over',
                        'leaved': True,
                        'leaved_msg': user.username + ' leaved the game',
                        'winners': winners,
                        'member': user.username,
                        'was_ready': True,
                        'state': game.room.get_state()
                    }
                    send_leave_msg(sp_id, msg)
                elif game.current_player == user:
                    players = game.players.filter(
                        entered=True, disable=False, leaved=False)
                    game.round += 1
                    if game.current >= game.players_playing:
                        game.current = 0
                        game.current_player = players[0].player
                    else:
                        game.current_player = players[game.current].player
                    game.time_stamp = time.time()
                    game.save()
                    msg = {
                        'action': 'leaved',
                        'leaved_msg': user.username + ' leaved the game',
                        'start': True, 'state': game.get_new_state(),
                        'member': user.username,
                        'was_ready': True}
                else:
                    game.save()
                    msg = {
                        'action': 'leaved',
                        'leaved_msg': user.username + ' leaved the game',
                        'start': False, 'member': user.username,
                        'was_ready': True
                    }
                send_leave_msg(sp_id, msg)
                return HttpResponse(json.dumps({'deleted': True, 'reason': 'You leaved the room'}))

            elif room.game.code == 'TAC':
                game = TAC.objects.get(game_id=sp_id)
                if game.zero == user:

                    game.room.reset()
                    game.delete()
                    msg = {
                        'action': 'leaved',
                        'player': 'O',
                        'player_name': user.username,
                        'member': user.username
                    }
                else:
                    game.room.reset()
                    game.delete()
                    msg = {
                        'action': 'leaved',
                        'player': 'X',
                        'player_name': user.username,
                        'member': user.username
                    }

                send_leave_msg(sp_id, msg)
                return HttpResponse(json.dumps({'deleted': True, 'reason': 'You leaved the room'}))

        # game not started

        member = Member.objects.filter(room=room).get(member=user)

        msg = {
            'action': 'leaved',
            'member': user.username,
            'was_ready': member.ready,
            'leaved_msg': user.username + ' leaved the room'
        }
        if member.ready:
            room.members_ready -= 1
        room.members_joined -= 1
        room.save()
        member.delete()
        send_leave_msg(sp_id, msg)
        return HttpResponse(json.dumps({
            'deleted': True, 'reason': 'You leaved the room'
        }))


def send_leave_msg(room_id, msg):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        room_id, {"type": "send_message", "text": json.dumps(msg)})
