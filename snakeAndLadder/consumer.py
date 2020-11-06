import json
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
# from account.models import User
from django.contrib.auth.models import User
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import threading
from .models import SNL, SNLPlayer, SNLMessage
from game.models import Member
import time
import random
from django.db.models import Q


async def run(room_no):

    '''
    take 15 sec time so that all player will join
    and start game when all are joined

    if some player is left dont join them

    '''

    channel_layer = get_channel_layer()
    await asyncio.sleep(15)
    data = await start(room_no)
    await channel_layer.group_send(
        room_no,
        {"type": "send_message", "text": json.dumps(data)},
    )


@database_sync_to_async
def start(room_no):
    '''
    start game form here

    '''
    data = {}
    try:
        game = SNL.objects.get(game_id=room_no)
    except:
        return {
            'action': 'error',
            'error_msg': 'Sorry, something went wrong, Refersh or restart the game'
        }

    if game.players_playing == 1:
        game.delete()
        game.room.reset()
        return {
            'action': 'player_not_joined',
        }
    game.start()
    data = {'action': 'started', 'state': game.get_new_state()}
    data['not_entered_players'] = [
        player.username for player in game.players.filter(entered=False)]
    return data


class SNLConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        # get room no from url
        self.room_no = self.scope['url_route']['kwargs']['room_no']
        username = self.scope['user'].username

        '''
        game default variables

        '''
        self.SNAKE_START = [43, 50, 56, 73, 84, 87, 98]
        self.LADDER_START = [2, 6, 20, 52, 57, 71]
        self.SNAKE_END = [17, 5, 8, 15, 63, 49, 40]
        self.LADDER_END = [23, 45, 59, 72, 96, 92]

        # self.SNAKE_START = []
        # self.LADDER_START = [2, 6, 20, 52, 57, 71]
        # self.SNAKE_END = []
        # self.LADDER_END = [23, 45, 59, 72, 96, 92]

        '''
        check weather game is started or not if started
        dont accept if the player hasnt joined earlier
        if game not started accept the request

        '''

        game_started = await self.check_started()
        if game_started:
            can_enter = await self.check_entered(username)

            # think About this point
            if not can_enter:

                # must be accepted first
                return await self.send({
                    "type": "websocket.disconnect"
                })

                '''
                await self.send({
                    "type": "websocket.send",
                    "text": json.dumps(
                        {
                            'action': 'cant_enter',
                            'error_msg': 'Due to network problem, try a new game'
                        }
                    )
                })
                await self.channel_layer.group_add(
                    self.room_no,
                    self.channel_name
                )

                '''

            else:
                state = await self.get_state()
                await self.send({
                    "type": "websocket.accept"
                })
                await self.send({
                    "type": "websocket.send",
                    "text": json.dumps(
                        {'action': 'again_entered',
                         'state': state,
                         }
                    )
                })

                await self.channel_layer.group_add(
                    self.room_no,
                    self.channel_name
                )
                await self.offline(username, True)
                await self.channel_layer.group_send(
                    self.room_no, {
                        'type': 'send_message',
                        'text': json.dumps({
                            'action': 'online',
                            'player': username,
                            'status': True
                        })
                    }
                )

        else:
            # game not started
            # create group or add in group
            await self.channel_layer.group_add(
                self.room_no,
                self.channel_name
            )

            await self.send({
                "type": "websocket.accept"
            })

            '''
            check member joined by check_run method
            if member joined is 0 then
            wait for 10 sec and start the game
            
            '''

            first_player = await self.check_run(username)
            if first_player:
                await run(self.room_no)

    async def websocket_receive(self, event):
        username = self.scope['user'].username
        msg = json.loads(event['text'])

        if msg['action'] == 'change_player':
            state = await self.change_player()

        elif msg['action'] == 'check_state':
            state = await self.check_state(msg['old_state'])

        elif msg['action'] == 'play':
            state = await self.play(username)

        elif msg['action'] == 'leave':
            state = await self.leave(username)
        elif msg['action'] == 'message':
            state = await self.message(username, msg['message'])

        await self.channel_layer.group_send(
            self.room_no, {
                'type': 'send_message',
                'text': json.dumps(state)
            }
        )

    async def websocket_disconnect(self, event):

        username = self.scope['user'].username

        await self.send({
            "type": "websocket.disconnect"
        })

        await self.offline(username, False)
        await self.channel_layer.group_send(
            self.room_no, {
                'type': 'send_message',
                        'text': json.dumps({
                            'action': 'online',
                            'player': username,
                            'status': False
                        })
            }
        )

    async def send_message(self, event):
        await self.send({
            "type": "websocket.send",
            "text": event['text']
        }
        )

    @database_sync_to_async
    def offline(self, username, status):
        game = SNL.objects.get(game_id=self.room_no)
        user = User.objects.get(username=username)
        player = game.players.get(player=user)
        player.online = status
        player.save()

    @database_sync_to_async
    def leave(self, username):
        game = SNL.objects.get(game_id=self.room_no)
        room = game.room
        user = User.objects.get(username=username)
        player = game.players.get(player=user)
        member = Member.objects.filter(room=room).get(member=user)
        player.leaved = True
        player.online = False
        game.players_playing -= 1
        room.members_joined -= 1
        room.members_ready -= 1
        member = Member.objects.filter(room=room).get(member=user)
        member.leaved = True
        player.save()
        member.save()
        players = game.players.filter(
            Q(entered=True) & Q(disable=False) & Q(leaved=False))
        if game.players_playing == 1:
            game.winner_state += 1
            players[0].rank = game.winner_state
            players[0].disable = True
            players[0].save()
            winners = [{'name': player.player.username,
                        'rank': player.rank}for player in game.players.filter(entered=True)]
            game.delete()
            room.game_url = ''
            room.members_joined -= 1
            room.members_ready -= 1
            room.started = False
            room.save()
            member.delete()
            return {
                'action': 'game_over',
                'leaved': True,
                'leaved_by': username,
                'winners': winners,
                'return_url': '/room/' + room.sp_id
            }

        if game.current_player == user:
            game.round += 1
            if game.current == game.players_playing:
                game.current = 0
                game.current_player = players[0].player
            else:
                game.current_player = players[game.current].player
            game.time_stamp = time.time()
            game.save()
            state = game.get_new_state()
            return{'action': 'leaved', 'leaved_by': username, 'start': True, 'state': state}
        else:
            return{'action': 'leaved', 'leaved_by': username, 'start': False}

    @database_sync_to_async
    def check_started(self):
        return SNL.objects.get(game_id=self.room_no).started

    @database_sync_to_async
    def check_entered(self, username):
        user = User.objects.get(username=username)
        game = SNL.objects.get(game_id=self.room_no)
        players = SNLPlayer.objects.filter(game=game)
        return players.get(player=user).entered

    @ database_sync_to_async
    def check_run(self, username):
        user = User.objects.get(username=username)
        game = SNL.objects.get(game_id=self.room_no)
        player = game.players.get(player=user)

        if not player.entered:
            player.entered = True
            player.save()
            if game.players_entered == 0:
                game.players_entered = 1
                game.players_playing = 1
                game.save()
                return True
            else:
                game.players_entered += 1
                game.players_playing += 1
                game.save()
                return False
        else:
            return False

    @database_sync_to_async
    def get_state(self):
        game = SNL.objects.get(game_id=self.room_no)
        state = game.get_state()
        if state['time'] < 0:
            # resume game
            game.time_stamp = time.time()
            game.save()
            state = game.get_new_state()
            state['resume'] = True
        else:
            state['resume'] = False
        return state

    @database_sync_to_async
    def message(self, username, text):
        game = SNL.objects.get(game_id=self.room_no)
        user = User.objects.get(username=username)
        msg = SNLMessage(user=user, game=game, text=text)
        msg.save()
        return {'action': 'message', 'sender': username, 'msg': text}

    @database_sync_to_async
    def check_state(self, state):
        game = SNL.objects.get(game_id=self.room_no)
        if game.match_state(state):
            game.current += 1
            if game.current == game.players_playing:
                game.current = 0
            game.current_player = SNLPlayer.objects.filter(Q(entered=True) and Q(
                disable=False) and Q(leaved=False))[game.current].player
            game.round += 1
            game.time_stamp = time.time()
            game.save()
            msg = {'action': 'set_state', 'error': True,
                   'state': game.get_new_state()}
        else:
            msg = {'action': 'set_state', 'error': False}
        return msg

    @database_sync_to_async
    def change_player(self):
        game = SNL.objects.get(game_id=self.room_no)
        players = game.players.filter(
            Q(entered=True) & Q(disable=False) & Q(leaved=False))
        game.current += 1
        if game.current == game.players_playing:
            game.current = 0
        game.current_player = players[game.current].player
        game.round += 1
        game.time_stamp = time.time()
        game.save()
        data = {'action': 'player_changed',
                'state': game.get_new_state()
                }

        return data

    @database_sync_to_async
    def play(self, username):
        '''
        check the player requesting is the 
        current player or not???        
        '''
        # get game
        game = SNL.objects.get(game_id=self.room_no)
        if game.current_player.username != username:
            return {
                'action': 'error', 'error_msg': 'wait for your turn'
            }
        game.round += 1
        game.time_stamp = time.time()
        user = User.objects.get(username=username)
        players = game.players.filter(
            Q(entered=True) & Q(disable=False) & Q(leaved=False))
        try:
            player = players.get(player=user)
        except:
            return {}
        # get a random no
        n = random.randint(1, 6)
        msg = {}

        # check if player can move or not
        # mean is it first move or not
        if player.can_move and not player.disable and not player.leaved:
            # then move
            # stop if position becomes greater than 100
            if (player.position + n <= 100):
                player.position += n
                if n != 6:
                    # move and change player
                    msg = {'action': 'move',
                           'player': game.current_player.username,
                           'number': n,
                           'position': player.position, 'win': False
                           }

                    if player.position == 100:
                        msg['win'] = True
                        game.winner_state += 1
                        player.rank = game.winner_state
                        msg['rank'] = player.rank
                        msg['winner'] = player.player.username
                        player.disable = True
                        game.players_playing -= 1
                        game.players_disabled += 1
                        player.save()
                        players = game.players.filter(
                            Q(entered=True) & Q(disable=False) & Q(leaved=False))
                        if game.players_playing == 1:
                            # game over
                            msg['action'] = 'game_over'
                            winners = [{'name': player.player.username,
                                        'rank': player.rank} for player in game.players.filter(entered=True)]

                            room = game.room
                            room.reset()
                            msg['url'] = room.sp_id
                            # delete game
                            game.delete()
                            msg['winners'] = winners
                            msg['leaved'] = False
                            return msg

                        if game.current == game.players_playing:
                            game.current = 0
                            game.current_player = players[0].player
                        else:
                            game.current_player = players[game.current].player

                    else:
                        game.current += 1
                        if game.current == game.players_playing:
                            game.current = 0
                        game.current_player = players[game.current].player

                    game.save()
                    player.save()
                    msg['state'] = game.get_new_state()

                else:
                    # move and dont change player because he got 6

                    msg = {'action': 'move', 'player': game.current_player.username,
                           'number': n, 'position': player.position, 'win': False}

                    if player.position == 100:
                        player.position -= n
                        msg['action'] = 'cant_move'
                        msg['error_msg'] = 'Invalid move, Try again in next turn'
                        game.current += 1
                        if game.current == game.players_playing:
                            game.current = 0
                        game.current_player = players[game.current].player
                    game.save()
                    player.save()
                    msg['state'] = game.get_new_state()

                # check snake and ladder

                if msg['position'] in self.SNAKE_START:
                    msg['bridge'] = 'SNAKE'
                    msg['action'] = 'double_move'
                    index = self.SNAKE_START.index(msg['position'])
                    player.position = self.SNAKE_END[index]
                    msg['bridge_end'] = self.SNAKE_END[index]
                    player.save()

                elif msg['position'] in self.LADDER_START:
                    msg['bridge'] = 'LADDER'
                    msg['action'] = 'double_move'
                    index = self.LADDER_START.index(msg['position'])
                    player.position = self.LADDER_END[index]
                    msg['bridge_end'] = self.LADDER_END[index]
                    player.save()
                return msg

            else:
                # cant move no beyond the limit
                game.current += 1
                if game.current == game.players_playing:
                    game.current = 0
                game.current_player = players[game.current].player
                game.save()
                msg = {'action': 'cant_move',
                       'error_msg': 'Step out of limit',
                       'number': n,
                       'player': username,
                       'state': game.get_new_state()}
                return msg
        else:
            # check if got six or not
            if n == 6:
                player.can_move = True
                player.save()
                msg = {'action': 'open', 'state': game.get_new_state(),
                       'number': n, 'player': username}
            else:
                # change player
                game.current += 1
                if game.current == game.players_playing:
                    game.current = 0
                game.current_player = game.players.filter(
                    Q(entered=True) & Q(disable=False) & Q(leaved=False))[game.current].player
                game.save()
                msg = {'action': 'cant_move', 'player': username, 'state': game.get_new_state(),
                       'number': n, 'error_msg': 'get 6 first to open'}
            return msg
