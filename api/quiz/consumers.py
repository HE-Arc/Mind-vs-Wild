import json
import random
import asyncio
import aiohttp
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from rest_framework.exceptions import AuthenticationFailed
from channels.db import database_sync_to_async
from urllib.parse import parse_qs
from rest_framework.authtoken.models import Token
from rooms.models import Room, RoomUser

# Dictionnaire global pour stocker l'état du jeu par room_id.
# Pour la production, pensez à utiliser un stockage persistant.
GAME_STATE = {}

class RoomQuizConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Connexion WebSocket : vérification du token, de la room et de l'appartenance.
        """
        query_params = parse_qs(self.scope["query_string"].decode())
        token = query_params.get('token', [None])[0]
        if not token:
            await self.close()
            return

        # Get user from token
        try:
            self.user = await self.get_user_from_token(token)
        except AuthenticationFailed:
            await self.close()
            return

        # Get room from URL path
        self.room_code = self.scope["url_route"]["kwargs"]["room_code"]
        room = await self.get_room_by_code(self.room_code)
        if room is None:
            await self.close()
            return

        self.room_id = room.id

        if self.user.is_anonymous:
            await self.close()
            return

        is_in_room = await self.user_in_room(self.room_id, self.user.id)
        if not is_in_room:
            await self.close()
            return

        self.room_group_name = f"room_{self.room_id}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Initialisation locale pour les infos statiques
        self.nb_participants = await self.count_participants(self.room_id)
        print(f"User {self.user.username} connected to room {self.room_id}")

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        if hasattr(self, 'user') and self.user:
            print(f"User {self.user.username} disconnected from room {getattr(self, 'room_id', '?')} code={close_code}")
        else:
            print(f"Un utilisateur non authentifié s'est déconnecté code={close_code}")

    async def get_user_from_token(self, token):
        try:
            token_obj = await database_sync_to_async(Token.objects.get)(key=token)
            return token_obj.user
        except Token.DoesNotExist:
            raise AuthenticationFailed("Token invalide ou expiré")

    async def receive(self, text_data):
        """
        Gestion des actions envoyées par les clients.
        """
        data = json.loads(text_data)
        action = data.get("action")

        if action == "start_game":
            # Charger les questions via l'API et initialiser l'état du jeu pour la room
            await self.load_questions_from_api()
            if not self.questions:
                await self.send(json.dumps({"error": "Aucune question trouvée via l'API"}))
                return

            # Initialisation de l'état global pour la room
            participants_ids = await self.get_participant_ids(self.room_id)
            GAME_STATE[self.room_id] = {
                "questions": self.questions,
                "current_question_index": 0,
                "answered_users": set(),
                "user_scores": {pid: 0 for pid in participants_ids}
            }

            # Diffuser la première question
            question_data = self.build_question_dict(GAME_STATE[self.room_id]["questions"][0])
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "send_question", "question": question_data}
            )

        elif action == "submit_answer":
            # Récupérer l'état partagé pour la room
            state = GAME_STATE.get(self.room_id)
            if not state:
                await self.send(json.dumps({"error": "La partie n'a pas démarré"}))
                return

            question_id = data.get("question_id")
            answer_text = data.get("answer_text")

            # Vérifier que la réponse concerne la question en cours
            current_q = state["questions"][state["current_question_index"]]
            if question_id != current_q["_id"]:
                await self.send(json.dumps({"error": "Mauvais ID de question"}))
                return

            # Vérifier si l'utilisateur a déjà répondu pour cette question
            if self.user.id in state["answered_users"]:
                await self.send(json.dumps({"error": "Déjà répondu"}))
                return

            # Vérifier la réponse
            is_correct = (answer_text['text'] == current_q["answer"])
            if is_correct:
                state["user_scores"][self.user.id] += 1

            state["answered_users"].add(self.user.id)

            # Envoyer le résultat individuel à l'utilisateur
            await self.send(json.dumps({
                "result": "correct" if is_correct else "incorrect",
                "score": state["user_scores"][self.user.id]
            }))

            # Calculer le nombre de joueurs restants et diffuser à tous
            players_left = self.nb_participants - len(state["answered_users"])
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "players_left", "players_left": players_left}
            )

            # Envoyer la mise à jour du score à tous les joueurs
            leaderboard = []
            sorted_scores = sorted(state["user_scores"].items(), key=lambda kv: kv[1], reverse=True)
            for user_id, score in sorted_scores:
                username = await self.get_username(user_id)
                leaderboard.append({"user_id": user_id, "username": username, "score": score})

            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "send_live_scores", "leaderboard": leaderboard}
            )

            # Si tout le monde a répondu, passer à la question suivante
            if len(state["answered_users"]) == self.nb_participants:
                await asyncio.sleep(1)  # délai avant de passer à la suite
                state["current_question_index"] += 1
                if state["current_question_index"] >= len(state["questions"]):
                    await self.end_game(state)
                    # Optionnel : supprimer l'état
                    GAME_STATE.pop(self.room_id, None)
                else:
                    state["answered_users"] = set()  # réinitialiser pour la nouvelle question
                    next_q = self.build_question_dict(state["questions"][state["current_question_index"]])
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {"type": "send_question", "question": next_q}
                    )
        else:
            await self.send(json.dumps({"error": "Action non reconnue"}))

    async def end_game(self, state):
        sorted_scores = sorted(state["user_scores"].items(), key=lambda kv: kv[1], reverse=True)
        leaderboard = []
        for user_id, score in sorted_scores:
            username = await self.get_username(user_id)
            leaderboard.append({"user_id": user_id, "username": username, "score": score})
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "send_scores", "leaderboard": leaderboard}
        )

    async def send_question(self, event):
        question_data = event["question"]
        await self.send(json.dumps({"action": "new_question", "question": question_data}))

    async def players_left(self, event):
        await self.send(json.dumps({"action": "players_left", "players_left": event["players_left"]}))

    async def send_scores(self, event):
        leaderboard = event["leaderboard"]
        await self.send(json.dumps({"action": "game_over", "leaderboard": leaderboard}))

    async def send_live_scores(self, event):
        leaderboard = event["leaderboard"]
        await self.send(json.dumps({"action": "live_scores", "leaderboard": leaderboard}))

    async def start_question_timer(self, question_id, duration=30):
        """Lance un timer pour la question courante"""
        state = GAME_STATE.get(self.room_id)
        if not state:
            return
            
        # Annoncer le démarrage du timer
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "send_timer_update", "seconds_left": duration, "question_id": question_id}
        )
        
        # Compter à rebours
        for seconds_left in range(duration-1, -1, -1):
            await asyncio.sleep(1)
            # Si tous les joueurs ont répondu, arrêter le timer
            if len(state["answered_users"]) == self.nb_participants:
                break
                
            # Si le jeu est terminé ou la question a changé, arrêter le timer
            if not GAME_STATE.get(self.room_id) or GAME_STATE[self.room_id]["current_question_index"] != state["current_question_index"]:
                break
                
            # Envoyer la mise à jour du timer
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "send_timer_update", "seconds_left": seconds_left, "question_id": question_id}
            )
        
        # Quand le timer expire, passer à la question suivante si nécessaire
        state = GAME_STATE.get(self.room_id)
        if state and state["current_question_index"] == state["current_question_index"]:
            # Traiter les joueurs qui n'ont pas répondu comme ayant donné une réponse incorrecte
            all_participants = set(await self.get_participant_ids(self.room_id))
            non_responders = all_participants - state["answered_users"]
            
            for user_id in non_responders:
                state["answered_users"].add(user_id)
                
            # Passer à la question suivante
            await self.move_to_next_question(state)

    async def send_timer_update(self, event):
        """Envoie la mise à jour du timer aux clients"""
        await self.send(json.dumps({
            "action": "timer_update", 
            "seconds_left": event["seconds_left"],
            "question_id": event["question_id"]
        }))

    @database_sync_to_async
    def user_in_room(self, room_id, user_id):
        return RoomUser.objects.filter(room_id=room_id, user_id=user_id).exists()

    @database_sync_to_async
    def count_participants(self, room_id):
        return RoomUser.objects.filter(room_id=room_id).count()

    @database_sync_to_async
    def get_room_by_code(self, room_code):
        try:
            return Room.objects.get(code=room_code)
        except Room.DoesNotExist:
            return None

    @database_sync_to_async
    def get_participant_ids(self, room_id):
        return list(RoomUser.objects.filter(room_id=room_id).values_list("user_id", flat=True))

    @database_sync_to_async
    def get_username(self, user_id):
        try:
            return User.objects.get(id=user_id).username
        except User.DoesNotExist:
            return "Unknown"

    async def load_questions_from_api(self):
        """
        Appelle l'API externe pour récupérer une liste de quiz.
        Stocke la liste retournée dans self.questions.
        """
        url = "https://quizzapi.jomoreschi.fr/api/v1/quiz?limit=5"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        quizzes = data.get("quizzes", [])
                        self.questions = quizzes
                    else:
                        print(f"Erreur API: status {response.status}")
                        self.questions = []
            except Exception as e:
                print("Erreur lors de l'appel à l'API:", e)
                self.questions = []

    def build_question_dict(self, question_obj):
        """
        Construit un dictionnaire formaté pour la question.
        """
        all_answers = [
            {"key": "A", "text": question_obj["answer"]},
            {"key": "B", "text": question_obj["badAnswers"][0]},
            {"key": "C", "text": question_obj["badAnswers"][1]},
            {"key": "D", "text": question_obj["badAnswers"][2]},
        ]
        random.shuffle(all_answers)
        return {
            "id": question_obj["_id"],
            "text": question_obj["question"],
            "options": all_answers,
            "difficulty": question_obj.get("difficulty"),
            "category": question_obj.get("category"),
        }
