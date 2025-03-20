<template>
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
