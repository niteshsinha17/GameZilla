from django.shortcuts import render, redirect
# from account.models import User
from django.contrib.auth.models import User
from game.models import Game, Room, Member
import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import authenticate
# Create your views here.


def home(request):
    user = request.user
    context = {}
    if user.is_authenticated:
        games = Game.objects.all()
        context['games'] = games
        return render(request, 'game/home.html', context)
    else:
        return redirect('register')


@login_required
def host_game(request, game_code):
    user = request.user
    game = Game.objects.get(code=game_code)
    room = Room(game=game, created_by=user)
    room.sp_id = user.username + '00' + str(Room.objects.all().count()+1)
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
        return render(request, 'game/no_room.html')

    if not (user.username == room.created_by.username):
        return render(request, 'game/not_allowed.html')
    members = Member.objects.filter(room=room)
    # check host is created or not as a member
    created = True
    try:
        member = members.get(member=user)
        member.online = True
        member.save()
    except:
        print('first time')
        created = False

    if not created:
        print('------------not created----------------')
        member = Member(member=user, host=True, ready=True)
        member.room = room
        member.save()
        room.members_joined += 1
        room.save()

    state = {
        'me': user.username,
        'game_code': room.game.code,
        'max_members': room.max_members,
        'members_joined': room.members_joined,
        'members_ready': room.members_ready,
        'room_no': sp_id
    }

    context['games'] = Game.objects.all()
    context['selected_game'] = room.game
    context['members'] = members
    context['state'] = json.dumps(state)
    context['me'] = member

    return render(request, 'game/room.html', context)


@login_required
def join_game(request, sp_id):
    context = {}
    user = request.user
    try:
        room = Room.objects.get(sp_id=sp_id)
    except:
        return render(request, 'game/no_room.html')
    members = Member.objects.filter(room=room)

    # check member is already created or not
    created = True
    try:
        member = members.get(member=user)
        member.online = True
        member.save()
    except:
        created = False

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

    state = {
        'me': user.username,
        'members_ready': room.members_ready,
        'room_no': sp_id
    }

    context['selected_game'] = room.game
    context['members'] = members
    context['state'] = json.dumps(state)
    context['me'] = member

    return render(request, 'game/join_room.html', context)
