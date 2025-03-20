import json
import random
import aiohttp

from channels.generic.websocket import AsyncWebsocketConsumer

class QuizConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        """Méthode appelée quand un client WebSocket se connecte."""
        # On accepte la connexion WebSocket
        await self.accept()
        # On peut envoyer un message de bienvenue
        await self.send(text_data=json.dumps({"status": "connected"}))

        # On va stocker dans l'instance la "dernière question" et la "bonne réponse"
        self.current_question_id = None
        self.current_correct_answer = None

    async def disconnect(self, close_code):
        """Méthode appelée quand le client se déconnecte."""
        print(f"WebSocket déconnecté (code: {close_code})")

    async def receive(self, text_data):
        """Méthode appelée à chaque message reçu du client."""
        data = json.loads(text_data)
        action = data.get("action")

        if action == "fetch_quiz":
            # Récupérer une question depuis l'API externe
            question_data = await self.fetch_random_question()
            if question_data is None:
                await self.send(json.dumps({"error": "Impossible de récupérer une question"}))
                return

            # Stocker l'ID et la bonne réponse, pour vérifier plus tard
            self.current_question_id = question_data["_id"]
            # On ne renvoie pas le champ 'answer' en clair, mais on la stocke pour vérifier
            self.current_correct_answer = question_data["answer"]

            # Construire la liste des 4 réponses [1 bonne, 3 mauvaises], puis mélanger
            all_answers = [
                {"key": "A", "text": question_data["answer"]},
                {"key": "B", "text": question_data["badAnswers"][0]},
                {"key": "C", "text": question_data["badAnswers"][1]},
                {"key": "D", "text": question_data["badAnswers"][2]},
            ]
            random.shuffle(all_answers)

            # Envoyer la question au client
            await self.send(json.dumps({
                "question": {
                    "id": question_data["_id"],
                    "question": question_data["question"],
                    "answers": all_answers,
                },
                "difficulty": question_data["difficulty"],
                "category": question_data["category"]
            }))

        elif action == "submit_answer":
            quiz_id = data.get("quizId")
            user_answer_key = data.get("answerKey")  # 'A', 'B', 'C' ou 'D'

            if quiz_id != self.current_question_id:
                # L'utilisateur n'a pas répondu à la bonne question (ou plus du tout la même)
                await self.send(json.dumps({"error": "Mauvais ID de question"}))
                return

            # On doit déterminer ce qui était la 'bonne' key.
            # On sait seulement 'self.current_correct_answer' = ex "Paris"
            # Or le client a envoyé user_answer_key (ex: 'C').
            # Pour vérifier, on doit se rappeler comment on a construit 'all_answers' plus haut.
            # => Soit on stocke un mapping 'key' -> 'text'.
            #    (Ici, on va demander au client de renvoyer aussi "answerText".)

            answer_text = data.get("answerText")
            # Compare la réponse à 'self.current_correct_answer'
            if answer_text == self.current_correct_answer:
                result = "correct"
            else:
                result = "incorrect"

            # Envoyer le résultat
            await self.send(json.dumps({
                "result": result,
                "correct_answer": self.current_correct_answer
            }))

            # (Optionnel) Envoyer la question suivante immédiatement

        else:
            # Action non reconnue
            await self.send(json.dumps({"error": "Action non reconnue"}))

    async def fetch_random_question(self):
        """Appelle l'API externe pour récupérer des quiz, puis renvoie un quiz au hasard."""
        url = "https://quizzapi.jomoreschi.fr/api/v1/quiz?limit=5"  # on peut ajouter &category=... &difficulty=... etc.

        # Appel HTTP en asynchrone avec aiohttp
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        quizzes = data.get("quizzes", [])
                        if not quizzes:
                            return None
                        # Choisir un quiz aléatoire
                        return random.choice(quizzes)
                    else:
                        print(f"Erreur API: status {response.status}")
                        return None
            except Exception as e:
                print("Erreur lors de l'appel à l'API:", e)
                return None
