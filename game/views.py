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
        member.online = True
        member.save()
    except:
        created = False

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
            return render(request, 'game/no_space.html')

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
    sp_id = request.POST.get('sp-id')
    return redirect('join', sp_id=sp_id)


@login_required
def leave(request, sp_id):
    try:
        room = Room.objects.get(sp_id=sp_id)
    except:
        return
    user = request.user
    member = Member.objects.filter(room=room).get(member=user)

    if member.host:
        if room.started:
            game = room.game.code
            if game == 'SNL':
                g = SNL.objects.get(game_id=sp_id)
                if g.players.filter(online=False) == g.max_player:
                    room.delete()
                    return HttpResponse(json.dumps({
                        'deleted': True,
                        'reason': 'Room deleted!'
                    }))
            elif game == "TAC":
                print('here tac')
                g = TAC.objects.get(game_id=sp_id)
                if not g.zero_active and not g.cross_active:
                    room.delete()
                    print('del')
                    return HttpResponse(json.dumps({
                        'deleted': True,
                        'reason': 'Room deleted!'
                    }))
            return HttpResponse(json.dumps({
                'deleted': False,
                'reason': 'other players playing. Please wait!'
            }))

        # room not started
        try:
            room.delete()
            leave_room(sp_id, user.username, remove_all=True)

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
        msg = {}
        # can move change krna hoga

        if room.started:
            if room.game.code == "SNL":
                game = SNL.objects.get(room=room)
            game.players_playing -= 1
            if game.players_playing == 1:
                game.winner_state += 1
                player = game.players.filter(
                    Q(entered=True) and Q(disable=False))
                player = player[0]
                player.rank = game.winner_state
                player.save()
                game.save()
                players = game.players.filter(entered=True)
                winners = [{'name': player.player.username,
                            'rank': player.rank} for player in players]

                room.game_url = ''
                room.started = False
                room.members_joined = game.players_playing
                room.members_ready = game.players_playing
                room.save()
                msg['url'] = room.sp_id

                # delete game and member
                game_id = game.game_id
                game.delete()
                member.delete()
                msg['winners'] = winners
                msg['action'] = 'game_over'
                leave_game(game_id, msg)
            else:
                player = game.players.get(user=user)
                player.disable = True
                player.leaved = True
                player.save()
                game.save()
                room.save()
                msg = {
                    'action': 'leaved',
                    'player': user.username
                }
                leave_game(game.game_id, msg)

            return HttpResponse(json.dumps({'deleted': True}))

        # game not started
        try:
            member.delete()
            room.members_joined -= 1
            room.save()
            leave_room(room.sp_id, user.username)
        except:
            return HttpResponse(json.dumps({
                'deleted': False,
                'reason': 'something went wrong'
            }))

        return HttpResponse(json.dumps({
            'deleted': True
        }))


def leave_room(room_id, username, remove_all=False):
    channel_layer = get_channel_layer()
    if remove_all is True:

        data = {
            'action': 'leaved',
            'member': 'all',
        }
    else:
        data = {
            'action': 'leaved',
            'member': username,
        }
    async_to_sync(channel_layer.group_send)(
        room_id, {"type": "send_message", "text": json.dumps(data)})


def leave_game(game_id, msg):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        game_id, {"type": "send_message", "text": json.dumps(msg)})
