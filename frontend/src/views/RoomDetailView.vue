<template>
  <q-page class="q-pa-md">
    <div v-if="room">
      <div class="text-center q-mb-md">
        <h2 class="text-h5 text-white text-bold q-ma-none">{{ room.name }}</h2>
        <div class="text-subtitle2 text-grey-7">Créé le: {{ new Date(room.created_at).toLocaleDateString() }}</div>
      </div>
      <h3>Participants ({{ room.participants.length }})</h3>
      <ul>
        <li v-for="p in room.participants" :key="p.id">{{ p.user.username }}</li>
      </ul>
  
      <q-btn color="negative" label="Quitter la Room" class="q-mt-md" @click="leaveRoom" />

      <!-- Ajouter avant le bouton "Lancer la partie" -->
      <q-expansion-item
        v-if="isHost"
        label="Options de jeu"
        icon="settings"
        header-class="text-primary"
      >
        <q-card>
          <q-card-section>
            <q-toggle v-model="gameOptions.eliminationMode" label="Mode élimination" />
            <q-slider
              v-model="gameOptions.questionTime"
              :min="10"
              :max="60"
              :step="5"
              label
              label-always
              class="q-mt-lg"
            >
              <template v-slot:thumb-label>{{ gameOptions.questionTime }}s</template>
            </q-slider>
            <div class="text-caption">Temps par question</div>

            <q-select
              v-model="gameOptions.difficulty"
              :options="['easy', 'medium', 'hard', 'mixed']"
              label="Difficulté"
              class="q-mt-md"
            />
          </q-card-section>
        </q-card>
      </q-expansion-item>

      <!-- Modifier le bouton pour passer les options -->
      <q-btn color="positive" label="Lancer la partie" class="q-ml-sm" @click="startGameWithOptions" />

      <!-- Zone du quiz en temps réel -->
      <div v-if="currentQuestion" class="q-mt-md">
        <q-card class="q-pa-md">
          <q-card-section>
            <p><strong>Question :</strong> {{ currentQuestion.text }}</p>
          </q-card-section>
          <q-card-section>
            <q-list bordered>
              <q-item v-for="(option, idx) in currentQuestion.options" :key="idx" clickable
                @click="submitAnswer(currentQuestion.id, option)">
                <q-item-section>
                  {{ option }}
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
        </q-card>
      </div>

      <!-- Ajouter dans la section quiz -->
      <div v-if="currentQuestion && timeLeft > 0" class="timer q-mt-sm">
        <q-linear-progress
          :value="timeLeft / maxTime"
          :color="timeLeft < 5 ? 'negative' : 'primary'"
          size="25px"
          class="q-mb-xs"
        >
          <div class="absolute-full flex flex-center">
            <q-badge color="white" text-color="black" :label="`${timeLeft}s`" />
          </div>
        </q-linear-progress>
      </div>

      <!-- Affichage du nombre de joueurs restants à répondre -->
      <div v-if="playersLeft > 0" class="q-mt-md">
        Il reste <strong>{{ playersLeft }}</strong> joueur(s) à répondre.
      </div>

      <!-- Scores finaux (leaderboard) -->
      <div v-if="leaderboard.length > 0" class="q-mt-md">
        <h3>Résultats finaux :</h3>
        <ul>
          <li v-for="(player, idx) in leaderboard" :key="idx">
            {{ player.username }} : {{ player.score }}
          </li>
        </ul>
      </div>

    </div>
    <div v-else class="text-center q-mt-md">
      <q-spinner size="50px" color="primary" />
      <p>Loading room details...</p>
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRoomStore } from '@/stores/room'
import { useQuasar } from 'quasar'
import { useAuthStore } from '@/stores/useAuthStore'


const route = useRoute()
const router = useRouter()
const roomStore = useRoomStore()
const authStore = useAuthStore() // Access the auth store
const $q = useQuasar()

const room = ref(null)
const message = ref(route.query.message || '')
// WebSocket
let socket = null

// Quiz states
const currentQuestion = ref(null)
const playersLeft = ref(0)
const leaderboard = ref([])

// Ajouter dans la section variables
const timeLeft = ref(0)
const maxTime = ref(30)

// Ajouter aux variables
const isHost = ref(false)
const gameOptions = ref({
  eliminationMode: false,
  questionTime: 30,
  difficulty: 'mixed'
})

/**
 * Charge les infos de la room via HTTP (REST).
 * Puis ouvre éventuellement le WS (si on veut l'ouvrir au montage).
 */
onMounted(async () => {
  const id = route.params.id
  room.value = await roomStore.fetchRoomDetails(id)
  if(message.value) {
    $q.notify({ type: 'positive', message: message.value })
  }
  isHost.value = computed(() => room.value?.created_by?.id === authStore.user?.id)
})


function leaveRoom() {
  roomStore.leaveRoom().then(() => {
    router.push('/rooms')
  })
}

// Ouvrir la connexion WebSocket
function connectWebSocket(callback) {
  if (socket) {
    callback && callback();
    return;
  }
  const token = authStore.token;
  if (!token) {
    message.value = "Utilisateur non authentifié"
    $q.notify({ type: 'negative', message: message.value })

    return
  }

  // Construire l'URL WebSocket avec le token
  const wsUrl = `${import.meta.env.VITE_WEBSOCKET_URL}/${room.value.id}/?token=${token}`
  socket = new WebSocket(wsUrl)

  socket.onopen = () => {
    console.log("WebSocket connecté - room", room.value.id);
    if (callback) callback(); // On envoie l'action dès que la connexion est ouverte
  };

  socket.onerror = (err) => {
    console.error("WebSocket error", err)

    message.value = "Erreur de connexion WebSocket"
    $q.notify({ type: 'negative', message: message.value })
  }

  socket.onclose = () => {
    console.log("WebSocket fermé")
    socket = null
  }

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data)
    console.log("Reçu WS:", data)

    if (data.error) {
      message.value = data.error
      $q.notify({ type: 'negative', message: message.value })
      return
    }

    switch (data.action) {
      case "new_question":
        currentQuestion.value = data.question
        // on reset playersLeft et leaderboard
        playersLeft.value = 0
        leaderboard.value = []
        break
      case "players_left":
        playersLeft.value = data.players_left
        break
      case "game_over":
        leaderboard.value = data.leaderboard
        currentQuestion.value = null
        break
      case "timer_update":
        timeLeft.value = data.seconds_left
        if (data.seconds_left === 30) maxTime.value = 30
        break
      default:
        console.log("Action WS non reconnue:", data.action)
    }
  }
}

// Remplacer startGame par cette fonction
function startGameWithOptions() {
  if (!socket) {
    connectWebSocket(() => {
      socket.send(JSON.stringify({ 
        action: "start_game",
        options: gameOptions.value
      }));
    });
  } else if (socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ 
      action: "start_game",
      options: gameOptions.value 
    }));
  }
}

// Méthode pour envoyer la réponse
function submitAnswer(questionId, answerText) {
  if (!socket) return
  socket.send(JSON.stringify({
    action: "submit_answer",
    question_id: questionId,
    answer_text: answerText
  }))
}
</script>
