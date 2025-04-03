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

# État global du jeu
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

        # Vérifier que l'utilisateur est dans la room
        is_in_room = await self.user_in_room(self.room_id, self.user.id)
        if not is_in_room:
            await self.close()
            return

        # Vérifier si l'utilisateur est admin
        self.is_admin = await self.is_room_admin(self.room_id, self.user.id)
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Notifier les autres participants de la connexion
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_joined",
                "user_id": self.user.id,
                "username": self.user.username
            }
        )

        # Envoyer l'état actuel si une partie est en cours
        state = GAME_STATE.get(self.room_id)
        if state and state.get('game_started'):
            current_q = None
            if 'current_index' in state and state['current_index'] >= 0:
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
            # Notifier les autres participants de la déconnexion
            if hasattr(self, 'user'):
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "user_left",
                        "user_id": self.user.id,
                        "username": self.user.username
                    }
                )
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get('action')

            if action == 'start_game':
                if not self.is_admin:
                    await self.send(json.dumps({
                        'error': 'Seul l\'administrateur peut démarrer la partie'
                    }))
                    return

                # Vérifier qu'une partie n'est pas déjà en cours
                if self.room_id in GAME_STATE and GAME_STATE[self.room_id].get('game_started'):
                    await self.send(json.dumps({
                        'error': 'Une partie est déjà en cours'
                    }))
                    return

                # Récupérer et valider les options
                try:
                    options = data.get('options', {})
                    question_count = max(1, min(30, int(options.get('questionCount', 5))))
                    timer_duration = max(10, min(60, int(options.get('questionTime', 30))))
                    elimination_mode = bool(options.get('eliminationMode', False))
                    category = options.get("category")
                except (ValueError, TypeError):
                    await self.send(json.dumps({
                        'error': 'Options de jeu invalides'
                    }))
                    return

                # Charger les questions
                success = await self.load_questions_from_api(question_count, category)
                if not success:
                    await self.send(json.dumps({
                        'error': 'Impossible de charger les questions'
                    }))
                    return

                # Initialiser l'état du jeu
                participant_ids = await self.get_room_participants(self.room_id)
                
                GAME_STATE[self.room_id] = {
                    'questions': self.questions,
                    'current_index': -1,
                    'scores': {pid: 0 for pid in participant_ids},
                    'answered': set(),
                    'timer_duration': timer_duration,
                    'time_remaining': timer_duration,
                    'elimination_mode': elimination_mode,
                    'active_players': set(participant_ids),
                    'game_started': True
                }

                # Notifier tous les participants du démarrage
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "game_starting",
                        "options": {
                            "question_count": question_count,
                            "timer_duration": timer_duration,
                            "elimination_mode": elimination_mode
                        }
                    }
                )

                # Envoyer la première question
                await self.send_next_question()

            elif action == 'submit_answer':
                if not self.room_id in GAME_STATE:
                    return

                state = GAME_STATE[self.room_id]
                if self.user.id in state['answered']:
                    return

                current_q = state['questions'][state['current_index']]
                question_id = data.get('question_id')
                answer = data.get('answer')  # Maintenant on reçoit la clé (A, B, C, D)
                
                # Récupérer la question actuelle
                if state['current_index'] < 0 or state['current_index'] >= len(state['questions']):
                    return
                
                current_q = state['questions'][state['current_index']]
                formatted_q = self.format_question(current_q)
                
                # Trouver l'option correspondant à la clé fournie
                selected_option = None
                correct_option = None
                for option in formatted_q['options']:
                    if option['key'] == answer:
                        selected_option = option
                    # Trouver aussi l'option correcte pour l'envoyer dans la réponse
                    if option['text'].lower() == current_q['answer'].lower():
                        correct_option = option
                
                if not selected_option:
                    return
                
                # Vérifier la réponse
                is_correct = selected_option['text'].lower() == current_q['answer'].lower()
                
                # Mettre à jour le score
                if is_correct:
                    state['scores'][self.user.id] = state['scores'].get(self.user.id, 0) + 10
                elif state['elimination_mode']:
                    state['active_players'].discard(self.user.id)

                state['answered'].add(self.user.id)
                
                # Envoyer le résultat au joueur
                await self.send(json.dumps({
                    'action': 'answer_result',
                    'correct': is_correct,
                    'selected_option': selected_option,
                    'correct_option': correct_option,
                    'points': state['scores'].get(self.user.id, 0)
                }))

                # Mettre à jour les scores pour tous
                await self.broadcast_scores()

                # Si tous les joueurs actifs ont répondu, passer à la suivante
                active_players = state['active_players']
                answered_active = len(state['answered'].intersection(active_players))
                if answered_active >= len(active_players):
                    await self.send_next_question()

        except json.JSONDecodeError:
            await self.send(json.dumps({
                'error': 'Format de message invalide'
            }))
        except Exception as e:
            print(f"Erreur dans receive: {str(e)}")
            await self.send(json.dumps({
                'error': 'Une erreur est survenue'
            }))

    def format_question(self, question):
        """Formate une question pour l'envoi aux clients"""
        if not question:
            return None
            
        options = [
            {'key': 'A', 'text': question['answer']},
            {'key': 'B', 'text': question['badAnswers'][0]},
            {'key': 'C', 'text': question['badAnswers'][1]},
            {'key': 'D', 'text': question['badAnswers'][2]}
        ]
        random.shuffle(options)

        return {
            'id': question['_id'],
            'text': question['question'],
            'options': options
        }

    async def broadcast_scores(self):
        """Envoie une mise à jour des scores à tous les participants"""
        state = GAME_STATE.get(self.room_id)
        if not state:
            return

        scores = []
        for user_id in state['active_players']:
            username = await self.get_username(user_id)
            scores.append({
                'user_id': user_id,
                'username': username,
                'score': state['scores'].get(user_id, 0),
                'is_active': True
            })

        # Ajouter les joueurs éliminés avec is_active = False
        eliminated = set(state['scores'].keys()) - state['active_players']
        for user_id in eliminated:
            username = await self.get_username(user_id)
            scores.append({
                'user_id': user_id,
                'username': username,
                'score': state['scores'].get(user_id, 0),
                'is_active': False
            })

        scores.sort(key=lambda x: x['score'], reverse=True)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'broadcast_scores_update',
                'scores': scores
            }
        )

    async def broadcast_scores_update(self, event):
        """Envoie une mise à jour des scores aux clients"""
        await self.send(json.dumps({
            'action': 'scores_update',
            'scores': event['scores']
        }))

    @database_sync_to_async
    def get_room_participants(self, room_id):
        """Récupère la liste des IDs des participants d'une room"""
        return list(RoomUser.objects.filter(room_id=room_id).values_list('user_id', flat=True))

    @database_sync_to_async
    def get_user_from_token(self, token):
        """Récupère l'utilisateur à partir du token"""
        return Token.objects.get(key=token).user

    @database_sync_to_async
    def user_in_room(self, room_id, user_id):
        """Vérifie si l'utilisateur est dans la room"""
        return RoomUser.objects.filter(room_id=room_id, user_id=user_id).exists()

    @database_sync_to_async
    def is_room_admin(self, room_id, user_id):
        """Vérifie si l'utilisateur est l'administrateur de la room"""
        try:
            room = Room.objects.get(id=room_id)
            return room.created_by_id == user_id
        except Room.DoesNotExist:
            return False

    async def game_starting(self, event):
        """Envoyé à tous les participants quand la partie démarre"""
        await self.send(json.dumps({
            "action": "game_starting",
            "settings": event["options"]
        }))

    async def send_next_question(self):
        """Envoie la question suivante à tous les participants"""
        state = GAME_STATE.get(self.room_id)
        if not state:
            return

        state['current_index'] += 1
        if state['current_index'] >= len(state['questions']):
            await self.end_game()
            return

        # Préparer la nouvelle question
        question = state['questions'][state['current_index']]
        formatted_q = self.format_question(question)
        state['answered'] = set()
        state['time_remaining'] = state['timer_duration']

        # Envoyer la question à tous
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'broadcast_question',
                'question': formatted_q,
                'time_remaining': state['timer_duration']
            }
        )

        # Démarrer le timer
        asyncio.create_task(self.run_timer())

    async def broadcast_question(self, event):
        """Envoie une question aux participants"""
        await self.send(json.dumps({
            'action': 'new_question',
            'question': event['question'],
            'time_remaining': event['time_remaining']
        }))

    async def run_timer(self):
        """Gère le décompte du temps pour la question en cours"""
        state = GAME_STATE.get(self.room_id)
        if not state:
            return

        # Réduire la fréquence des mises à jour du timer pour diminuer le trafic réseau
        # On n'envoie maintenant les mises à jour que toutes les 3 secondes au lieu de chaque seconde
        update_interval = 3  
        remaining_time = state['time_remaining']
        
        while remaining_time > 0:
            for _ in range(min(update_interval, remaining_time)):
                await asyncio.sleep(1)
                remaining_time -= 1
                state['time_remaining'] = remaining_time
                
                # Vérifier si tous les joueurs ont répondu
                if len(state['answered'].intersection(state['active_players'])) >= len(state['active_players']):
                    break
        
            # Si tous les joueurs ont répondu, on sort de la boucle
            if len(state['answered'].intersection(state['active_players'])) >= len(state['active_players']):
                break
                
            # Envoyer la mise à jour du timer moins fréquemment
            # Les clients gèrent leur propre timer localement, donc nous n'avons pas besoin 
            # d'envoyer des mises à jour trop fréquentes
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'broadcast_timer',
                    'time_remaining': remaining_time
                }
            )

        # Si le temps est écoulé ou tous ont répondu, passer à la suivante
        if remaining_time <= 0:
            await self.send_next_question()

    async def broadcast_timer(self, event):
        """Envoie une mise à jour du timer aux clients"""
        await self.send(json.dumps({
            'action': 'timer_update',
            'time_remaining': event['time_remaining']
        }))

    async def end_game(self):
        """Termine la partie et envoie les scores finaux"""
        state = GAME_STATE.get(self.room_id)
        if not state:
            return

        # Préparer les scores finaux
        final_scores = []
        for user_id in state['scores'].keys():
            username = await self.get_username(user_id)
            final_scores.append({
                'user_id': user_id,
                'username': username,
                'score': state['scores'].get(user_id, 0),
                'is_active': user_id in state['active_players']
            })

        final_scores.sort(key=lambda x: x['score'], reverse=True)

        # Envoyer les résultats finaux
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'broadcast_game_over',
                'scores': final_scores
            }
        )

        # Nettoyer l'état du jeu
        if self.room_id in GAME_STATE:
            del GAME_STATE[self.room_id]

    async def broadcast_game_over(self, event):
        """Envoie les résultats finaux aux clients"""
        await self.send(json.dumps({
            'action': 'game_over',
            'final_scores': event['scores']
        }))

    async def load_questions_from_api(self, limit=5, category=None):
        """Charge les questions depuis l'API"""
        url = f'https://quizzapi.jomoreschi.fr/api/v1/quiz?limit={limit}'
        if category:
            url += f"&category={category}"
        print(url)
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.questions = data.get('quizzes', [])[:limit]
                        return len(self.questions) > 0
                    else:
                        print(f"Erreur API: status {response.status}")
                        return False
            except Exception as e:
                print(f"Erreur lors du chargement des questions: {str(e)}")
                return False
        return False

    @database_sync_to_async
    def get_username(self, user_id):
        """Récupère le nom d'utilisateur à partir de l'ID"""
        try:
            user = User.objects.get(id=user_id)
            return user.username
        except User.DoesNotExist:
            return "Utilisateur inconnu"
            
    async def user_joined(self, event):
        """Envoyé quand un utilisateur rejoint la room"""
        await self.send(json.dumps({
            "action": "participant_joined",
            "user_id": event["user_id"],
            "username": event["username"]
        }))
        
    async def user_left(self, event):
        """Envoyé quand un utilisateur quitte la room"""
        await self.send(json.dumps({
            "action": "participant_left",
            "user_id": event["user_id"],
            "username": event["username"]
        }))
