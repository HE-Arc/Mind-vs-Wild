import json
import random
import asyncio
import aiohttp
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from urllib.parse import parse_qs
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rooms.models import Room, RoomUser

GAME_STATE = {}

class RoomQuizConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        query_params = parse_qs(self.scope["query_string"].decode())
        token = query_params.get('token', [None])[0]

        if not token:
            await self.close()
            return

        try:
            self.user = await self.get_user_from_token(token)
        except Token.DoesNotExist:
            await self.close()
            return

        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'room_{self.room_id}'

        if not await self.user_in_room(self.room_id, self.user.id):
            await self.close()
            return

        self.is_admin = await self.is_room_admin(self.room_id, self.user.id)

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        await self.channel_layer.group_send(self.room_group_name, {
            "type": "user_joined",
            "user_id": self.user.id,
            "username": self.user.username
        })

        state = GAME_STATE.get(self.room_id)
        if state and state.get('game_started'):
            current_q = None
            if state['current_index'] >= 0:
                current_q = self.format_question(state['questions'][state['current_index']])
            await self.send(json.dumps({
                "action": "game_state",
                "state": {
                    "is_started": True,
                    "current_question": current_q,
                    "time_remaining": state.get('time_remaining'),
                    "scores": state.get('scores', {})
                }
            }))

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            if hasattr(self, 'user'):
                await self.channel_layer.group_send(self.room_group_name, {
                    "type": "user_left",
                    "user_id": self.user.id,
                    "username": self.user.username
                })
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get('action')
            if action == 'start_game':
                await self.handle_start_game(data)
            elif action == 'submit_answer':
                await self.handle_submit_answer(data)
        except Exception as e:
            await self.send(json.dumps({'error': str(e)}))

    async def handle_start_game(self, data):
        if not self.is_admin:
            return await self.send(json.dumps({'error': "Seul l'admin peut démarrer le jeu"}))

        if self.room_id in GAME_STATE and GAME_STATE[self.room_id].get('game_started'):
            return await self.send(json.dumps({'error': "Partie déjà en cours"}))

        options = data.get('options', {})
        qcount = max(1, min(30, int(options.get('questionCount', 5))))
        qtime = max(10, min(60, int(options.get('questionTime', 30))))
        elimination = bool(options.get('eliminationMode', False))
        category = options.get("category")

        if not await self.load_questions(qcount, category):
            return await self.send(json.dumps({'error': "Chargement des questions échoué"}))

        users = await self.get_room_participants(self.room_id)
        GAME_STATE[self.room_id] = {
            'questions': self.questions,
            'current_index': -1,
            'scores': {uid: 0 for uid in users},
            'answered': set(),
            'timer_duration': qtime,
            'time_remaining': qtime,
            'elimination_mode': elimination,
            'active_players': set(users),
            'game_started': True,
            'lock': asyncio.Lock()
        }

        await self.channel_layer.group_send(self.room_group_name, {
            "type": "game_starting",
            "options": {
                "question_count": qcount,
                "timer_duration": qtime,
                "elimination_mode": elimination
            }
        })
        await self.send_next_question()

    async def handle_submit_answer(self, data):
        state = GAME_STATE.get(self.room_id)
        if not state or self.user.id in state['answered']:
            return

        q = state['questions'][state['current_index']]
        ans = data.get('answer')
        correct = ans and ans.lower() == q['answer'].lower()

        if correct:
            state['scores'][self.user.id] += 10
        elif state['elimination_mode']:
            state['active_players'].discard(self.user.id)

        state['answered'].add(self.user.id)

        await self.send(json.dumps({
            'action': 'answer_result',
            'correct': correct,
            'selected_option': ans,
            'correct_option': q['answer'],
            'points': state['scores'][self.user.id]
        }))
        await self.broadcast_scores()

        if state['answered'].issuperset(state['active_players']):
            await asyncio.sleep(2)
            await self.send_next_question()

    async def send_next_question(self):
        state = GAME_STATE.get(self.room_id)
        if not state:
            return

        async with state['lock']:
            state['current_index'] += 1
            if (state['elimination_mode'] and len(state['active_players']) == 1 
                or state['current_index'] >= len(state['questions'])):
                return await self.end_game()

            q = state['questions'][state['current_index']]
            state['answered'] = set()
            state['time_remaining'] = state['timer_duration']

            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'broadcast_question',
                'question': self.format_question(q),
                'time_remaining': state['timer_duration']
            })

            asyncio.create_task(self.run_timer(state['current_index']))

    async def run_timer(self, q_index):
        state = GAME_STATE.get(self.room_id)
        while state['time_remaining'] > 0:
            await asyncio.sleep(1)
            if state['current_index'] != q_index:
                return
            state['time_remaining'] -= 1
            if state['time_remaining'] % 3 == 0:
                await self.channel_layer.group_send(self.room_group_name, {
                    'type': 'broadcast_timer',
                    'time_remaining': state['time_remaining']
                })

        if state['current_index'] == q_index:
            await asyncio.sleep(2)
            if state['elimination_mode']:
                unanswered_players = state['active_players'] - state['answered']
                state['active_players'].difference_update(unanswered_players)
                await self.broadcast_scores()
                
                if len(state['active_players']) == 1:
                     return await self.end_game()
                 
            await self.send_next_question()

    async def broadcast_scores(self):
        state = GAME_STATE.get(self.room_id)
        scores = []
        for uid in state['scores']:
            username = await self.get_username(uid)
            scores.append({
                'user_id': uid,
                'username': username,
                'score': state['scores'][uid],
                'is_active': uid in state['active_players']
            })
        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'broadcast_scores_update', 'scores': sorted(scores, key=lambda x: x['score'], reverse=True)
        })

    async def end_game(self):
        state = GAME_STATE.get(self.room_id)
        final = []
        for uid in state['scores']:
            username = await self.get_username(uid)
            final.append({
                'user_id': uid,
                'username': username,
                'score': state['scores'][uid],
                'is_active': uid in state['active_players']
            })
        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'broadcast_game_over',
            'scores': sorted(final, key=lambda x: x['score'], reverse=True)
        })
        del GAME_STATE[self.room_id]

    def format_question(self, question):
        options = [question['answer']] + question['badAnswers']
        random.shuffle(options)
        return {'id': question['_id'], 'text': question['question'], 'options': options}

    async def broadcast_question(self, event):
        await self.send(json.dumps({'action': 'new_question', 'question': event['question'], 'time_remaining': event['time_remaining']}))

    async def broadcast_timer(self, event):
        await self.send(json.dumps({'action': 'timer_update', 'time_remaining': event['time_remaining']}))

    async def broadcast_scores_update(self, event):
        await self.send(json.dumps({'action': 'scores_update', 'scores': event['scores']}))

    async def broadcast_game_over(self, event):
        await self.send(json.dumps({'action': 'game_over', 'final_scores': event['scores']}))

    async def game_starting(self, event):
        await self.send(json.dumps({'action': 'game_starting', 'settings': event['options']}))

    async def user_joined(self, event):
        await self.send(json.dumps({'action': 'participant_joined', 'user_id': event['user_id'], 'username': event['username']}))

    async def user_left(self, event):
        await self.send(json.dumps({'action': 'participant_left', 'user_id': event['user_id'], 'username': event['username']}))

    async def load_questions(self, limit, category):
        url = f'https://quizzapi.jomoreschi.fr/api/v1/quiz?limit={limit}' + (f"&category={category}" if category else '')
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.questions = data.get('quizzes', [])[:limit]
                        return bool(self.questions)
        except:
            return False
        return False

    @database_sync_to_async
    def get_user_from_token(self, token):
        return Token.objects.get(key=token).user

    @database_sync_to_async
    def user_in_room(self, room_id, user_id):
        return RoomUser.objects.filter(room_id=room_id, user_id=user_id).exists()

    @database_sync_to_async
    def is_room_admin(self, room_id, user_id):
        try:
            return Room.objects.get(id=room_id).created_by_id == user_id
        except Room.DoesNotExist:
            return False

    @database_sync_to_async
    def get_room_participants(self, room_id):
        return list(RoomUser.objects.filter(room_id=room_id).values_list('user_id', flat=True))

    @database_sync_to_async
    def get_username(self, user_id):
        try:
            return User.objects.get(id=user_id).username
        except User.DoesNotExist:
            return "Utilisateur inconnu"
