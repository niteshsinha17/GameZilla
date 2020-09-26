import json
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
# from account.models import User
from django.contrib.auth.models import User
from game.models import *
from snakeAndLadder.models import *
import random


class RoomConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        self.room_no = self.scope['url_route']['kwargs']['room_no']

        # get username from scope
        username = self.scope['user'].username

        is_member = await self.check_member(username)
        if is_member:
            # create group or add in group
            await self.channel_layer.group_add(
                self.room_no,
                self.channel_name
            )
            await self.send({
                "type": "websocket.accept"
            })

            is_entered = await self.check_entered(username)
            print(is_entered)
            if not is_entered:
                data = await self.add_player(username)
                await self.channel_layer.group_send(
                    self.room_no, {
                        "type": "send_message",
                        "text": json.dumps(data)
                    }
                )
            data = await self.online(username, True)
            await self.channel_layer.group_send(
                self.room_no, {
                    "type": "send_message",
                    "text": json.dumps(data)
                }
            )

    async def websocket_receive(self, event):
        print("recieve", event)
        username = self.scope['user'].username

        is_member = self.check_member(username)
        if not is_member:
            return

        msg = json.loads(event['text'])
        is_host = await self.check_host(username)
        if msg['action'] == 'start':
            # must be sent by host

            if not is_host:
                # not a host return
                return

            # start the game
            data = await self.start_game()

        elif msg['action'] == 'change_game':
            # must be sent by host
            if not is_host:
                # not a host return
                return

            # change game
            data = await self.change_game(msg)

        elif msg['action'] == 'remove_player':
            # must be sent by host
            if not is_host:
                print('not host')
                # not a host return
                return

            data = await self.remove_member(msg)

        elif msg['action'] == 'change_ready':
            # must be sent by other member
            if is_host:
                return
            if not is_member:
                return
            data = await self.change_ready(username)

        elif msg['action'] == 'leave':
            # must be sent by other member
            if not is_member:
                return
            data = await self.leave(username, is_host)
            # await self.send({
            #     "type": "websocket.disconnect"
            # })

        await self.channel_layer.group_send(
            self.room_no, {
                "type": "send_message",
                "text": json.dumps(data)
            }
        )

    async def websocket_disconnect(self, event):
        username = username = self.scope['user'].username
        is_member = self.check_member(username)
        if not is_member:
            return
        await self.send({
            "type": "websocket.disconnect"
        })
        data = await self.online(username, False)
        await self.channel_layer.group_send(
            self.room_no, {
                "type": "send_message",
                "text": json.dumps(data)
            }
        )

    async def send_message(self, event):
        await self.send({
            "type": "websocket.send",
            "text": event['text']
        }
        )

    @database_sync_to_async
    def online(self, username, status):
        user = User.objects.get(username=username)
        room = Room.objects.get(sp_id=self.room_no)
        members = Member.objects.filter(room=room)
        member_ = members.get(member=user)
        member_.online = status
        member_.save()
        return {'action': 'online', 'member': username, 'status': status}

    @database_sync_to_async
    def change_ready(self,  username):
        user = User.objects.get(username=username)
        room = Room.objects.get(sp_id=self.room_no)
        members = Member.objects.filter(room=room)
        member_ = members.get(member=user)
        member_.ready = not member_.ready
        member_.save()
        if member_.ready == True:
            room.members_ready += 1
        else:
            room.members_ready -= 1

        room.save()
        data = {
            'action': 'ready',
            'member': username,
            'state': member_.ready
        }
        return data

    @database_sync_to_async
    def check_entered(self,  username):
        print('-----------check entered')
        user = User.objects.get(username=username)
        room = Room.objects.get(sp_id=self.room_no)
        members = Member.objects.filter(room=room)
        member_ = members.get(member=user)
        if member_.entered:
            return True
        else:
            member_.entered = True
            member_.save()
            return False

    @database_sync_to_async
    def check_member(self, username):
        print('-----------------check member------------------')
        user = User.objects.get(username=username)
        room = Room.objects.get(sp_id=self.room_no)
        is_member = True
        try:
            members = Member.objects.filter(room=room)
            members.get(member=user)
        except:
            is_member = False

        return is_member

    @database_sync_to_async
    def check_host(self, username):
        user = User.objects.get(username=username)
        room = Room.objects.get(sp_id=self.room_no)
        is_host = True
        try:
            members = Member.objects.filter(room=room)
            m = members.get(member=user)
            is_host = m.host
        except:
            print('accept')
            is_host = False

        print(is_host)

        return is_host

    @database_sync_to_async
    def leave(self, username, is_host):
        print('-----------leave---------------')
        if is_host:
            Room.objects.get(self.room_no).delete()
            return {'action': 'leaved', 'member': 'all'}
        else:
            user = User.objects.get(username=username)
            room = Room.objects.get(sp_id=self.room_no)
            members = Member.objects.filter(room=room)
            m = members.get(member=user)
            if m.ready:
                room.members_ready -= 1
            room.members_joined -= 1
            room.save()
            m.delete()
        return {'action': 'leaved', 'member': username}

    @database_sync_to_async
    def add_player(self, username):
        user = User.objects.get(username=username)
        room = Room.objects.get(sp_id=self.room_no)
        members = Member.objects.filter(room=room)
        m = members.get(member=user)
        return {
            'action': 'add_member',
            'member': username,
            'ready': m.ready,
            'host': m.host
        }

    @database_sync_to_async
    def remove_member(self, msg):
        print('-------------remove member-----------')
        user = User.objects.get(username=msg['member'])
        room = Room.objects.get(sp_id=self.room_no)
        members = Member.objects.filter(room=room)
        m = members.get(member=user)
        data = {}
        data['was_ready'] = False
        if m.ready:
            room.members_ready -= 1
            data['was_ready'] = True
        m.delete()
        room.members_joined -= 1
        room.save()

        data = {
            'action': 'member_removed',
            'member': msg['member']
        }
        return data

    @database_sync_to_async
    def change_game(self, msg):
        print('--------------change game--------------')
        new_game_code = msg['code']
        new_game = Game.objects.get(code=new_game_code)
        room = Room.objects.get(sp_id=self.room_no)
        if new_game.max_player >= room.members_joined:
            data = {'action': 'game_changed',
                    'changed': True,
                    'new_code': new_game_code,
                    'name': new_game.game_name,
                    'max_members': new_game.max_player
                    }
            data['url'] = msg['url']
            data['old_code'] = room.game.code
            room.max_members = new_game.max_player
            room.game = new_game
            room.save()

        else:
            data = {'action': 'game_changed',
                    'changed': False,
                    'error': 'Members size exceeded'}
        return data

    @database_sync_to_async
    def start_game(self):
        print('---------------start--------------')
        room = Room.objects.get(sp_id=self.room_no)
        if room.members_joined <= 1:
            return {'action': 'started',
                    'can_start': False,
                    'error': 'Min 2 players required'}
        if not (room.members_joined > 1 and room.members_joined == room.members_ready):

            return {'action': 'started',
                    'can_start': False,
                    'error': 'All players not ready'}

        code = room.game.code
        room.started = True
        room.save()

        if code == 'SNL':
            game = SNL(room=room, max_player=room.members_joined)
            game.game_id = str(room.created_by.username) + \
                'SNL00' + str(SNL.objects.all().count()+1)

            colors = ['RED', 'BLUE', 'YELLOW', 'GREEN']
            members = Member.objects.filter(room=room)
            game.current_player = members[random.randint(
                0, game.max_player-1)].member
            game.save()
            for i in range(game.max_player):
                player = SNLPlayer(
                    game=game, player=members[i].member, color=colors[i])
                player.save()
            url = '/SNL/'+game.game_id+'/'

            return {'action': 'started', 'can_start': True, 'url': url}
