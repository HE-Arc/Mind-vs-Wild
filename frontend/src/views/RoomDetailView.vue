<template>
  <q-page class="q-pa-md">
    <div v-if="room" class="row q-col-gutter-md">

      <!-- Contenu principal -->
      <div class="col-12">
        <!-- Afficher la salle d'attente uniquement si le jeu n'a pas commencé -->
        <div v-if="!gameStarted">
          <div class="text-center q-mb-md">
            <h2 class="text-h5 text-white text-bold q-ma-none">{{ room.name }}</h2>
          </div>
        </div>

        <!-- Scores -->
        <q-card v-if="leaderboard.length > 0" class="scores-card text-black" style="background-color: white;">
          <q-card-section>
            <div class="text-h6">Scores</div>
            <q-list>
              <q-item v-for="(player, idx) in leaderboard" :key="idx" class="q-mb-sm">
                <q-item-section avatar>
                  <q-avatar :color="getPlayerColor(idx)" text-color="white">
                    {{ player.username.charAt(0).toUpperCase() }}
                  </q-avatar>
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ player.username }}</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-chip :color="getPlayerColor(idx)" text-color="white" class="score-chip">
                    {{ player.score }} pts
                  </q-chip>
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
        </q-card>

        <div v-if="!gameStarted">
          <!-- Liste d'attente des joueurs -->
          <q-card class="waiting-room q-mb-md">
            <q-card-section style="background-color: white;">
              <div class="text-h6">Liste d'attente ({{ room.participants.length }})</div>
              <div class="row q-col-gutter-sm">
                <div v-for="p in room.participants" :key="p.id" class="col-6 col-sm-4 col-md-3">
                  <q-card class="player-card" :class="{ 'host-card': p.user.id === room.created_by.id }">
                    <q-card-section class="text-center">
                      <q-avatar size="50px" color="primary" text-color="white">
                        {{ p.user.username.charAt(0).toUpperCase() }}
                      </q-avatar>
                      <div class="text-subtitle1 q-mt-sm">{{ p.user.username }}</div>
                      <q-badge v-if="p.user.id === room.created_by.id" color="positive">Hôte</q-badge>
                    </q-card-section>
                  </q-card>
                </div>
              </div>
            </q-card-section>
          </q-card>

          <!-- Configuration du jeu (visible uniquement pour l'hôte) -->
          <q-slide-transition v-if="isHost">
            <q-card class="config-card">
              <q-card-section>
                <div class="text-h6">Configuration de la partie</div>
                <q-toggle v-model="gameOptions.eliminationMode" label="Mode élimination" />
                <q-select
                  v-model="gameOptions.questionCount"
                  :options="[5, 10, 15, 20, 25, 30]"
                  label="Nombre de questions"
                  class="q-mb-md"
                />
                <q-slider
                  v-model="gameOptions.questionTime"
                  :min="10"
                  :max="60"
                  :step="5"
                  label
                  label-always
                >
                  <template v-slot:thumb-label>{{ gameOptions.questionTime }}s</template>
                </q-slider>
                <div class="text-caption">Temps par question</div>
                <q-select
                  v-model="gameOptions.difficulty"
                  :options="[
                    { label: 'Facile', value: 'easy' },
                    { label: 'Moyen', value: 'medium' },
                    { label: 'Difficile', value: 'hard' },
                    { label: 'Mixte', value: 'mixed' }
                  ]"
                  label="Difficulté"
                  class="q-mt-md"
                />
                  
              <q-select
                v-model="gameOptions.category"
                :options="categoryOptions"
                label="Catégorie"
                class="q-mt-md"
              />
                <div class="text-center q-mt-md">
                  <q-btn color="positive" label="Lancer la partie" @click="startGameWithOptions" />
                </div>
              </q-card-section>
            </q-card>
          </q-slide-transition>

          <!-- Message d'attente pour les non-admins -->
          <div v-if="!isHost" class="text-center q-mt-md">
            <q-card class="waiting-message">
              <q-card-section>
                <q-icon name="hourglass_empty" color="primary" size="48px" class="q-mb-md" />
                <h6 class="text-h6 q-ma-none">En attente du lancement de la partie</h6>
                <p class="text-subtitle1 q-ma-none">L'hôte de la partie configurera et lancera bientôt le jeu</p>
              </q-card-section>
            </q-card>
          </div>
          <q-btn color="negative" label="Quitter la Room" class="q-mt-md" @click="leaveRoom" />
        </div>

        <quiz-view
          v-else
          :current-question="currentQuestion"
          :time-left="timeLeft"
          :max-time="maxTime"
          :last-result="lastAnswer ? (lastAnswer.correct ? 'correct' : 'incorrect') : null"
          :correct-answer="lastAnswer?.correctOption?.key"
          :selected-answer="lastAnswer?.option?.key"
          @submit-answer="submitAnswer"
        />
      </div>
    </div>

    <div v-else class="text-center q-mt-md">
      <q-spinner size="50px" color="primary" />
      <p>Loading room details...</p>
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRoomStore } from '@/stores/room'
import { useQuasar } from 'quasar'
import { useAuthStore } from '@/stores/auth'
import QuizView from './QuizView.vue'

const route = useRoute()
const router = useRouter()
const roomStore = useRoomStore()
const authStore = useAuthStore()
const $q = useQuasar()

const room = ref(null)
const message = ref(route.query.message || '')
// WebSocket variables
let socket = null
const wsStatus = ref('disconnected')
const wsError = ref(null)

// Quiz states
const currentQuestion = ref(null)
const playersLeft = ref(0)
const leaderboard = ref([])
const answerSubmitted = ref(false)
const lastAnswer = ref(null)
const timeLeft = ref(0)
const maxTime = ref(30)

// Timer variables
let timerInterval = null
let questionEndTime = 0

// Host and game configuration
const isHost = ref(false)
const categories = ref([])
const categoryOptions = computed(() =>
  categories.value.map(category => ({ label: category.label, value: category.value }))
)
const gameOptions = ref({
  eliminationMode: false,
  questionTime: 30,
  difficulty: 'mixed',
  category: null,
  questionCount: 10
})

// Game state
const isGameStarting = ref(false)
const gameStarted = ref(false)

onMounted(async () => {
  const id = route.params.id
  try {
    room.value = await roomStore.fetchRoomDetails(id)
    if(message.value) {
      $q.notify({ type: 'positive', message: message.value })
    }
    
    // Vérifier si l'utilisateur actuel est l'hôte de la salle
    isHost.value = room.value?.created_by?.id === authStore.user?.id
    const response = await fetch('/categories.json');
    categories.value = await response.json();
    // Établir la connexion WebSocket
    connectWebSocket()
  } catch (error) {
    console.error('Erreur lors du chargement de la room:', error)
    $q.notify({ 
      type: 'negative', 
      message: 'Impossible de charger les détails de la room' 
    })
  }
})

onUnmounted(() => {
  // Arrêter le timer local
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
  
  // Fermer proprement la connexion WebSocket lors de la sortie du composant
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.close()
  }
})

function leaveRoom() {
  // Arrêter le timer
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
  
  // Fermer la connexion WebSocket avant de quitter
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.close()
  }
  
  roomStore.leaveRoom().then(() => {
    router.push('/rooms')
  })
}

// Fonction simplifiée pour établir la connexion WebSocket
function connectWebSocket() {
  // Si une connexion existe déjà, ne rien faire
  if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) {
    return
  }
  
  wsStatus.value = 'connecting'
  wsError.value = null
  
  const token = authStore.token
  if (!token) {
    wsError.value = "Utilisateur non authentifié"
    wsStatus.value = 'error'
    $q.notify({ type: 'negative', message: wsError.value })
    return
  }

  try {
    const wsUrl = `${import.meta.env.VITE_WEBSOCKET_URL}/${room.value.id}/?token=${token}`
    socket = new WebSocket(wsUrl)

    socket.onopen = () => {
      console.log("WebSocket connecté - room", room.value.id)
      wsStatus.value = 'connected'
      wsError.value = null
    }

    socket.onerror = (err) => {
      console.error("WebSocket error", err)
      wsError.value = "Erreur de connexion WebSocket"
      wsStatus.value = 'error'
      $q.notify({ 
        type: 'negative', 
        message: 'Erreur de connexion au serveur de jeu',
        actions: [{
          label: 'Reconnecter',
          color: 'white',
          handler: () => connectWebSocket()
        }]
      })
    }

    socket.onclose = () => {
      console.log("WebSocket fermé")
      wsStatus.value = 'disconnected'
      socket = null
      
      // Proposer une reconnexion manuelle, pas de boucle
      if (room.value) {
        $q.notify({
          type: 'warning',
          message: 'Connexion au serveur de jeu perdue',
          actions: [{
            label: 'Reconnecter',
            color: 'white',
            handler: () => connectWebSocket()
          }]
        })
      }
    }

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      console.log("Reçu WS:", data)

      if (data.error) {
        $q.notify({ type: 'negative', message: data.error })
        return
      }

      switch (data.action) {
        case 'game_state':
          handleGameState(data)
          break
        case 'game_starting':
          handleGameStarting(data)
          break
        case 'participant_joined':
          handleParticipantJoined(data)
          break
        case 'participant_left':
          handleParticipantLeft(data)
          break
        case 'new_question':
          handleNewQuestion(data)
          break
        case 'timer_update':
          handleTimerUpdate(data)
          break
        case 'scores_update':
          handleScoresUpdate(data)
          break
        case 'game_over':
          handleGameOver(data)
          break
        // Ajouter un gestionnaire pour l'événement "answer_result"
        case 'answer_result':
          handleAnswerResult(data)
          break
      }
    }
  } catch (err) {
    console.error('Erreur lors de la création du WebSocket:', err)
    wsError.value = "Erreur lors de la création de la connexion"
    wsStatus.value = 'error'
    $q.notify({ 
      type: 'negative', 
      message: 'Impossible de se connecter au serveur de jeu',
      actions: [{
        label: 'Réessayer',
        color: 'white',
        handler: () => connectWebSocket()
      }]
    })
  }
}

// Gestionnaires d'événements WebSocket
function handleGameState(data) {
  if (data.state?.is_started) {
    gameStarted.value = true
    currentQuestion.value = data.state.current_question
    timeLeft.value = data.state.time_remaining
    if (data.state.scores) {
      leaderboard.value = Object.entries(data.state.scores).map(([id, score]) => ({
        id,
        username: getPlayerUsername(id),
        score
      }))
    }
  }
}

function handleGameStarting(data) {
  isGameStarting.value = true
  
  // Mettre à jour les options du jeu avec les paramètres reçus
  if (data.settings) {
    // Stocker le timer_duration configuré pour l'utiliser plus tard
    if (data.settings.timer_duration) {
      gameOptions.value.questionTime = data.settings.timer_duration
    }
    
    // Autres options
    if (data.settings.question_count) {
      gameOptions.value.questionCount = data.settings.question_count
    }
    
    if (data.settings.elimination_mode !== undefined) {
      gameOptions.value.eliminationMode = data.settings.elimination_mode
    }
  }
  
  $q.notify({
    type: 'info',
    message: 'La partie va bientôt commencer...'
  })
}

function handleParticipantJoined(data) {
  if (!room.value.participants.find(p => p.user.id === data.user_id)) {
    room.value.participants.push({
      user: {
        id: data.user_id,
        username: data.username
      }
    })
    $q.notify({
      type: 'positive',
      message: `${data.username} a rejoint la partie`
    })
  }
}

function handleParticipantLeft(data) {
  const index = room.value.participants.findIndex(p => p.user.id === data.user_id)
  if (index !== -1) {
    room.value.participants.splice(index, 1)
    $q.notify({
      type: 'warning',
      message: `${data.username} a quitté la partie`
    })
  }
}

function handleNewQuestion(data) {
  gameStarted.value = true
  isGameStarting.value = false
  currentQuestion.value = data.question
  
  // Définir le temps maximal selon la configuration de la room
  const configuredTime = gameOptions.value.questionTime;
  maxTime.value = configuredTime;
  
  // Réinitialiser l'UI
  answerSubmitted.value = false;
  lastAnswer.value = null;
  
  // Démarrer un timer purement local
  startLocalTimer(configuredTime);
  
  console.log(`Nouvelle question: temps configuré=${configuredTime}s`);
}

function handleTimerUpdate(data) {
  // Ne rien faire - on laisse le timer local gérer le temps
  // On ne fait que logger l'information pour le débogage
  console.log(`Timer serveur: ${data.time_remaining}s, timer local: ${timeLeft.value}s`);
}

// Fonction pour démarrer un timer local fluide
function startLocalTimer(initialTime) {
  // Nettoyer tout timer existant
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
  
  // Calculer le moment précis où le timer se terminera
  questionEndTime = Date.now() + (initialTime * 1000)
  timeLeft.value = initialTime
  
  // Créer un intervalle pour mettre à jour le timer toutes les 100ms (pour une animation fluide)
  timerInterval = setInterval(() => {
    // Calculer le temps restant en secondes
    const remainingMs = questionEndTime - Date.now()
    const remainingSecs = Math.ceil(remainingMs / 1000)
    
    // Mettre à jour le temps restant
    if (remainingSecs <= 0) {
      timeLeft.value = 0
      clearInterval(timerInterval)
      timerInterval = null
    } else {
      timeLeft.value = remainingSecs
    }
  }, 100)
}

// Nettoyer le timer lors de la fin de partie
function handleGameOver(data) {
  // Arrêter le timer
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
  
  gameStarted.value = false
  currentQuestion.value = null
  leaderboard.value = data.final_scores
  $q.notify({
    type: 'positive',
    message: 'Partie terminée !',
    timeout: 2000
  })
}

function handleScoresUpdate(data) {
  // Mettre à jour le tableau des scores avec les données du serveur
  leaderboard.value = data.scores.map(playerScore => ({
    id: playerScore.user_id,
    username: playerScore.username,
    score: playerScore.score,
    isActive: playerScore.is_active
  }))
}

function handleAnswerResult(data) {
  answerSubmitted.value = true
  lastAnswer.value = {
    option: data.selected_option,
    correct: data.correct,
    correctOption: data.correct_option
  }
  
  // Notification du résultat
  $q.notify({
    type: data.correct ? 'positive' : 'negative',
    message: data.correct ? 'Bonne réponse !' : 'Mauvaise réponse !',
    timeout: 2000
  })
}

// Fonction pour récupérer le nom d'utilisateur à partir de l'ID
function getPlayerUsername(userId) {
  const participant = room.value?.participants.find(p => p.user.id === userId)
  return participant?.user.username || "Joueur inconnu"
}

// Fonction pour démarrer le jeu (uniquement pour l'hôte)
function startGameWithOptions() {
  // Vérification que l'utilisateur est bien l'hôte
  if (!isHost.value) {
    $q.notify({
      type: 'negative',
      message: 'Seul l\'hôte peut lancer la partie'
    })
    return
  }
  
  // Vérification de la connexion WebSocket
  if (!socket || socket.readyState !== WebSocket.OPEN) {
    $q.notify({
      type: 'negative',
      message: 'Connexion au serveur perdue. Veuillez rafraîchir la page.'
    })
    return
  }
  
  // Envoi de la demande de démarrage du jeu
  socket.send(JSON.stringify({
    action: 'start_game',
    options: {
        ...gameOptions.value,
        category: gameOptions.value.category?.value
      }
  }))
  
  // Notification de démarrage
  $q.notify({
    type: 'positive',
    message: 'Démarrage de la partie...'
  })
}

// Fonction pour envoyer une réponse à une question
function submitAnswer(questionId, option) {
  if (!socket || socket.readyState !== WebSocket.OPEN) {
    $q.notify({
      type: 'negative',
      message: 'Connexion au serveur perdue'
    })
    return
  }
  
  answerSubmitted.value = true
  lastAnswer.value = { option, correct: false }
  
  socket.send(JSON.stringify({
    action: 'submit_answer',
    question_id: questionId,
    answer: option.key
  }))
}

// Couleurs pour les joueurs
function getPlayerColor(index) {
  const colors = ['primary', 'purple', 'deep-orange', 'green', 'blue', 'red']
  return colors[index % colors.length]
}
</script>

<style lang="scss">
.waiting-room {
  background: rgba(255, 255, 255, 0.05);
  .player-card {
    background: rgba(255, 255, 255, 0.1);
    transition: all 0.3s ease;
    &:hover {
      transform: translateY(-2px);
    }
    &.host-card {
      border: 2px solid var(--q-positive);
    }
  }
}

.config-card {
  background: rgba(255, 255, 255, 0.05);
}

.quiz-card {
  background: rgba(255, 255, 255, 0.05);
}

.scores-card {
  background: rgba(255, 255, 255, 0.05);
  position: sticky;
  top: 16px;
  .score-chip {
    min-width: 80px;
    justify-content: center;
  }
}

.waiting-message {
  background: rgba(255, 255, 255, 0.05);
  max-width: 500px;
  margin: 0 auto;
  text-align: center;
}

.q-badge {
  font-size: 0.8rem;
  padding: 4px 8px;
}
</style>
