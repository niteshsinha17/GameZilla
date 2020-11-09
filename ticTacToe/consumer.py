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
from .models import TAC, TACMessage
from game.models import Member
import time


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
        game = TAC.objects.get(game_id=room_no)
    except:
        return {
            'action': 'error',
            'error_msg': 'Sorry, something went wrong, Refersh or restart the game'
        }
    if game.players_entered == 1:
        game.delete()
        if game.zero_entered:
            player = game.zero.username
        else:
            player = game.cross.username
        game.room.reset()
        return {
            'action': 'player_not_joined',
            'player': player
        }
    game.start()
    data = {'action': 'started', 'board': game.board,
            'state': game.get_new_state()}
    return data


class TACConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        # get room no from url
        self.room_no = self.scope['url_route']['kwargs']['room_no']
        username = self.scope['user'].username

        '''
        check weather game is started or not if started
        dont accept if the player hasnt joined earlier
        if game not started accept the request

        '''
        can_enter = await self.can_enter(username)
        if not can_enter:
            return

        game_started = await self.check_started()
        if game_started:
            state = await self.get_state()
            await self.send({
                "type": "websocket.accept"
            })
            await self.send({
                "type": "websocket.send",
                "text": json.dumps(
                    {
                        'action': 'again_entered',
                        'state': state['state'],
                        'board': state['board']

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

    async def websocket_receive(self, event):
        username = self.scope['user'].username
        msg = json.loads(event['text'])

        if msg['action'] == 'change_player':
            data = await self.change_player()

        elif msg['action'] == 'check_state':
            data = await self.check_state(msg['old_state'])

        elif msg['action'] == 'play':
            data = await self.play(msg, username)

        elif msg['action'] == 'leave':
            data = await self.leave(username)

        elif msg['action'] == 'message':
            data = await self.message(username, msg['message'])

        await self.channel_layer.group_send(
            self.room_no, {
                'type': 'send_message',
                'text': json.dumps(data)
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
        try:
            game = TAC.objects.get(game_id=self.room_no)
        except:
            return
        user = User.objects.get(username=username)
        if user == game.zero:
            game.zero_active = status
        else:
            game.cross_active = status
        game.save()

    @database_sync_to_async
    def leave(self, username):
        game = TAC.objects.get(game_id=self.room_no)
        if game.zero.username == username:
            game.room.reset()
            game.delete()
            return {'action': 'leaved', 'winner': 'X'}
        else:
            return {'action': 'leaved', 'winner': 'O'}

    @database_sync_to_async
    def check_started(self):
        return TAC.objects.get(game_id=self.room_no).started

    @database_sync_to_async
    def can_enter(self, username):
        game = TAC.objects.get(game_id=self.room_no)
        return username == game.zero.username or username == game.cross.username

    @ database_sync_to_async
    def check_run(self, username):
        user = User.objects.get(username=username)
        game = TAC.objects.get(game_id=self.room_no)

        if not game.zero_entered and not game.cross_entered:
            if user == game.zero:
                game.zero_entered = True
            else:
                game.cross_entered = True
            game.players_entered += 1
            game.save()
            return True
        elif (game.zero_entered and not game.cross_entered) or (game.cross_entered and not game.zero_entered):
            if game.zero_entered:
                game.cross_entered = True
            else:
                game.zero_entered = True
            game.players_entered += 1
            game.save()
            return False
        else:
            return False

    @database_sync_to_async
    def get_state(self):
        game = TAC.objects.get(game_id=self.room_no)
        state = game.get_state()
        state = game.get_state()
        if state['time'] < 0:
            # resume game
            game.time_stamp = time.time()
            game.save()
            state = game.get_new_state()
            state['resume'] = True
        else:
            state['resume'] = False
        return {'state': state, 'board': game.board}

    @database_sync_to_async
    def message(self, username, text):
        game = TAC.objects.get(game_id=self.room_no)
        user = User.objects.get(username=username)
        msg = TACMessage(user=user, game=game, text=text)
        msg.save()
        return {'action': 'message', 'sender': username, 'msg': text}

    @database_sync_to_async
    def check_state(self, state):
        game = TAC.objects.get(game_id=self.room_no)
        if game.match_state(state):
            game.current = 1-game.current
            if game.current == 0:
                game.current_player = game.zero
            else:
                game.current_player = game.cross
            game.time_stamp = time.time()
            game.round += 1
            game.save()
            msg = {'action': 'set_state', 'error': True, 'board': game.board,
                   'state': game.get_new_state()}
        else:
            msg = {'action': 'set_state', 'error': False}
        return msg

    @database_sync_to_async
    def change_player(self):
        game = TAC.objects.get(game_id=self.room_no)
        game.current = 1-game.current
        if game.current == 0:
            game.current_player = game.zero
        else:
            game.current_player = game.cross
        game.time_stamp = time.time()
        game.round += 1
        game.save()
        data = {'action': 'player_changed', 'board': game.board,
                'state': game.get_new_state()
                }
        return data

    @database_sync_to_async
    def play(self, msg, username):
        '''
        check the player requesting is the 
        current player or not???        
        '''
        # get game
        game = TAC.objects.get(game_id=self.room_no)
        if game.current_player.username != username:
            return {
                'action': 'error', 'error_msg': 'wait for your turn'
            }
        i = msg['i']
        j = msg['j']
        game.round += 1
        game.time_stamp = time.time()
        if game.current_player.username != username:
            return{'action': 'error', 'error_msg': 'wait for your turn'}
        if game.board[i][j] != 0:
            return {
                'action': 'error', 'error_msg': 'Invalid move'
            }
        if game.zero.username == username:
            game.board[i][j] = 'Z'
        else:
            game.board[i][j] = 'X'
        game.save()
        data = game.check_win()

        if data['win']:
            data['player'] = username
            data['winner'] = game.board[i][j]
            data['i'] = i
            data['j'] = j
            data['board'] = game.board
            game.room.reset()
            game.delete()
        elif data['action'] == 'game_over':
            data['player'] = username
            data['i'] = i
            data['j'] = j
            data['board'] = game.board
            game.room.reset()
            game.delete()
        else:
            data['player'] = username
            data['i'] = i
            data['j'] = j
            game.current = 1-game.current
            if game.current == 0:
                game.current_player = game.zero
            else:
                game.current_player = game.cross
            game.save()
            data['board'] = game.board
            data['state'] = game.get_new_state()
        return data
