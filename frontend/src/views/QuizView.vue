<template>
    <q-page class="q-page">
        <div class="header">
            <q-icon name="person" class="player-icon" />
            <span class="player-count">1 joueur</span>
        </div>

        <q-card class="timer-card">
            <q-card-section class="q-pa-none timer-text">
                <q-icon name="hourglass_empty" class="timer-icon" />
                00:00
            </q-card-section>
        </q-card>

        <q-card>
            <q-card-section class="q-pa-none card-question">
                Quelle est la capitale du japon?
            </q-card-section>
        </q-card>
        <div class="answer">
            <div class="column left-column">
                <q-card class="card-spacing">
                    <q-card-section class="q-pa-none card-answer">
                        Kyoto
                    </q-card-section>
                </q-card>
                <q-card class="card-spacing">
                    <q-card-section class="q-pa-none card-answer">
                        Tokyo
                    </q-card-section>
                </q-card>
            </div>
            <div class="column right-column">
                <q-card class="card-spacing">
                    <q-card-section class="q-pa-none card-answer">
                        Osaka
                    </q-card-section>
                </q-card>
                <q-card class="card-spacing">
                    <q-card-section class="q-pa-none card-answer">
                        Nagoya
                    </q-card-section>
                </q-card>
            </div>
        </div>
    </q-page>
</template>

<style scoped>
.q-page {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: auto;
    padding: 20px;
    position: relative;
}

.header {
    position: absolute;
    top: 10px;
    left: 10px;
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: #3F6182;
    padding: 10px;
    border-radius: 5px;
    color: white;
    width: auto;
}

.timer-card {
    position: absolute;
    top: 10px;
    right: 10px;
    background-color: #3F6182;
    color: white;
    padding: 10px;
    border-radius: 5px;
    display: flex;
    align-items: center;
    justify-content: center;
    width: auto;
}

.timer-icon {
    margin-right: 5px;
}

.player-icon {
    margin-right: 5px;
}

.answer {
    display: flex;
    flex-direction: column;
    width: 100%;
    margin-top: 20px;
}

.column {
    width: 100%;
    margin-bottom: 10px;
}

.card-answer {
    background-color: #3F6182;
    width: 100%;
    padding: 16px;
    cursor: pointer;
    text-align: center;
}

.card-question {
    background-color: #3F6182;
    width: 100%;
    padding: 16px;
    text-align: center;
}

.card-spacing {
    margin-top: 10px;
    margin-bottom: 10px;
}

@media (min-width: 768px) {
    .q-page {
        height: 75vh;
    }

    .answer {
        flex-direction: row;
        justify-content: space-between;
        padding: 0 20px;
    }

    .column {
        flex: 1;
        margin-bottom: 0;
        padding: 10px;
    }

    .left-column {
        background-color: #EE7154;
    }

    .right-column {
        background-color: #EE7154;
    }
}
</style>
  <q-page class="q-pa-md">
    <h2>Quiz via WebSocket + API Externe</h2>

    <!-- Affichage des éventuelles erreurs (API ou WS) -->
    <q-banner v-if="error" class="bg-negative text-white q-mb-md">
      {{ error }}
    </q-banner>

    <!-- Affichage du résultat de la dernière réponse -->
    <q-banner v-if="lastResult"
      :class="{ 'bg-positive': lastResult === 'correct', 'bg-negative': lastResult === 'incorrect' }"
      class="text-white q-mb-md">
      Votre dernière réponse est {{ lastResult === 'correct' ? 'CORRECTE' : 'INCORRECTE' }}
      <span v-if="correctAnswer">
        (Bonne réponse : {{ correctAnswer }})
      </span>
    </q-banner>

    <!-- Affichage de la question courante -->
    <div v-if="currentQuestion">
      <q-card class="q-pa-md q-mb-md bg-dark text-white">
      <q-card-section>
        <p class="text-bold">Question : {{ currentQuestion.question }}</p>
        <p>Catégorie : {{ category }}</p>
        <p>Difficulté : {{ difficulty }}</p>
      </q-card-section>
      <q-card-section>
        <q-list bordered>
        <q-item v-for="(answer, index) in currentQuestion.answers" :key="answer.key" clickable
          @click="selectAnswer(currentQuestion.id, answer.key, answer.text)" class="text-white">
          <q-item-section>
          {{ answer.key }} - {{ answer.text }}
          </q-item-section>
        </q-item>
        </q-list>
      </q-card-section>
      </q-card>
    </div>

    <!-- Bouton pour demander une nouvelle question (on peut le faire après la réponse) -->
    <q-btn label="Nouvelle question" color="primary" @click="fetchQuiz" />

  </q-page>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const socketUrl = 'ws://127.0.0.1:8000/ws/quiz/'; // => re_path(r'^ws/quiz/$', ...)

let socket = null;
const error = ref(null);

// Question courante
const currentQuestion = ref(null);
const difficulty = ref('');
const category = ref('');

// Résultat de la dernière réponse
const lastResult = ref(null);
const correctAnswer = ref(null);

function connectWebSocket() {
  socket = new WebSocket(socketUrl);

  socket.onopen = () => {
    console.log('WebSocket connecté');
    // On peut fetch la première question immédiatement
    fetchQuiz();
  };

  socket.onerror = (err) => {
    console.error('Erreur WebSocket', err);
    error.value = 'Connexion WebSocket échouée';
  };

  socket.onclose = () => {
    console.log('WebSocket déconnecté');
  };

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Reçu:', data);

    if (data.error) {
      error.value = data.error;
    }
    else if (data.question) {
      // Une nouvelle question
      currentQuestion.value = data.question;
      difficulty.value = data.difficulty || '';
      category.value = data.category || '';
      // On reset le résultat précédent
      lastResult.value = null;
      correctAnswer.value = null;
    }
    else if (data.result) {
      // On a reçu le verdict sur la dernière réponse
      lastResult.value = data.result; // "correct" ou "incorrect"
      correctAnswer.value = data.correct_answer; // ex: "Paris"
    }
  };
}

// Envoyer l'action "fetch_quiz" au serveur
function fetchQuiz() {
  if (!socket || socket.readyState !== WebSocket.OPEN) {
    console.log("WebSocket non ouvert !");
    return;
  }
  socket.send(JSON.stringify({ action: 'fetch_quiz' }));
}

// Envoyer la réponse choisie
function selectAnswer(quizId, answerKey, answerText) {
  console.log(`Réponse envoyée pour quiz ${quizId}: key=${answerKey} text=${answerText}`);
  socket.send(JSON.stringify({
    action: 'submit_answer',
    quizId,
    answerKey,
    answerText
  }));
}

onMounted(() => {
  connectWebSocket();
});

onUnmounted(() => {
  if (socket) {
    socket.close();
  }
});
</script>

<style scoped>
.text-bold {
  font-weight: bold;
}
</style>
