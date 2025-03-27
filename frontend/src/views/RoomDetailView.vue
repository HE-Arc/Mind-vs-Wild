<template>
  <q-page class="q-pa-md">
    <div v-if="room">
      <div class="text-center q-mb-md">
        <h2 class="text-h5 text-white text-bold q-ma-none">{{ room.name }}</h2>
        <div class="text-subtitle2 text-grey-7">Code: {{ room.code }}</div>
      </div>

      <h3>Participants ({{ room.participants.length }})</h3>
      <ul>
        <li v-for="p in room.participants" :key="p.id">
          {{ p.user.username }}
        </li>
      </ul>

      <q-btn color="negative" label="Quitter la Room" class="q-mt-md" @click="leaveRoom" />

      <!-- Lancer le quiz -->
      <q-btn color="positive" label="Lancer la partie" class="q-ml-sm" @click="startGame" />

      <!-- Zone d'erreur / messages WebSocket -->
      <q-banner v-if="errorMsg" class="q-mt-md" :class="{ 'bg-negative text-white': true }">
        {{ errorMsg }}
      </q-banner>

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
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRoomStore } from '@/stores/room'
import { useAuthStore } from '@/stores/useAuthStore'

// Imports pour la logique
const route = useRoute()
const router = useRouter()
const roomStore = useRoomStore()
const authStore = useAuthStore() // Access the auth store

const room = ref(null)
const errorMsg = ref(null)

// WebSocket
let socket = null

// Quiz states
const currentQuestion = ref(null)
const playersLeft = ref(0)
const leaderboard = ref([])

/**
 * Charge les infos de la room via HTTP (REST).
 * Puis ouvre éventuellement le WS (si on veut l'ouvrir au montage).
 */
onMounted(async () => {
  const code = route.params.code
  room.value = await roomStore.fetchRoomDetails(code)

  if (!room.value) {
    console.error("Room introuvable")
    return
  }

  // => Option 1 : ouvrir la WebSocket tout de suite
  // connectWebSocket()

  // => Option 2 : on attend que l'user clique "Lancer la partie" pour ouvrir la WS
})

function leaveRoom() {
  roomStore.leaveRoom().then(() => {
    router.push('/rooms')
  })
}

// Ouvrir la connexion WebSocket
function connectWebSocket() {
  if (socket) {
    return
  }

  // Récupérer le token d'authentification
  const token = authStore.token
  if (!token) {
    errorMsg.value = "Utilisateur non authentifié"
    return
  }

  // Construire l'URL WebSocket avec le token
  const wsUrl = `${import.meta.env.VITE_WEBSOCKET_URL}/${room.value.code}/?token=${token}`
  socket = new WebSocket(wsUrl)

  socket.onopen = () => {
    console.log("WebSocket connecté - room", room.value.id)
  }

  socket.onerror = (err) => {
    console.error("WebSocket error", err)
    errorMsg.value = "Erreur de connexion WebSocket"
  }

  socket.onclose = () => {
    console.log("WebSocket fermé")
    socket = null
  }

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data)
    console.log("Reçu WS:", data)

    if (data.error) {
      errorMsg.value = data.error
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
      default:
        console.log("Action WS non reconnue:", data.action)
    }
  }
}

// Méthode pour lancer la partie
function startGame() {
  // on ouvre la WS si pas déjà fait
  if (!socket) {
    connectWebSocket()
  }
  // envoie l'action "start_game"
  socket.send(JSON.stringify({ action: "start_game" }))
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
