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

        <div v-if="lastResult" class="result-message"
            :class="{ 'correct': lastResult === 'correct', 'incorrect': lastResult === 'incorrect' }">
            <span v-if="lastResult === 'correct'">Bonne réponse !</span>
            <span v-else>Réponse incorrecte. La bonne réponse est {{ correctAnswer }}.</span>
        </div>

        <q-card v-if="currentQuestion">
            <q-card-section class="q-pa-none card-question">
                {{ currentQuestion.question }}
            </q-card-section>
        </q-card>

        <div v-if="currentQuestion" class="answer">
            <div class="column left-column">
                <q-card v-for="answer in leftAnswers" :key="answer.key" class="card-spacing" :class="{
                    'correct-answer': answer.key === correctAnswer,
                    'wrong-answer': lastResult === 'incorrect' && selectedAnswer === answer.key
                }" @click="selectAnswer(currentQuestion.id, answer.key, answer.text)">
                    <q-card-section class="q-pa-none card-answer">
                        {{ answer.text }}
                    </q-card-section>
                </q-card>
            </div>
            <div class="column right-column">
                <q-card v-for="answer in rightAnswers" :key="answer.key" class="card-spacing" :class="{
                    'correct-answer': lastResult === 'correct' && answer.key === correctAnswer,
                    'wrong-answer': lastResult === 'incorrect' && selectedAnswer === answer.key
                }" @click="selectAnswer(currentQuestion.id, answer.key, answer.text)">
                    <q-card-section class="q-pa-none card-answer">
                        {{ answer.text }}
                    </q-card-section>
                </q-card>
            </div>
        </div>
    </q-page>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';

const socketUrl = 'ws://127.0.0.1:8000/ws/quiz/';
let socket = null;

const currentQuestion = ref(null);
const error = ref(null);
const lastResult = ref(null);
const correctAnswer = ref(null);
const selectedAnswer = ref(null);

function connectWebSocket() {
    socket = new WebSocket(socketUrl);

    socket.onopen = () => {
        console.log('WebSocket connecté');
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
        } else if (data.question) {
            currentQuestion.value = data.question;
            lastResult.value = null;
            correctAnswer.value = null;
            selectedAnswer.value = null;
        } else if (data.result) {
            lastResult.value = data.result;
            correctAnswer.value = data.correct_answer;
        }
    };
}

function fetchQuiz() {
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ action: 'fetch_quiz' }));
    }
}

function selectAnswer(quizId, answerKey, answerText) {
    if (selectedAnswer.value !== null) {
        return;
    }

    if (socket && socket.readyState === WebSocket.OPEN) {
        selectedAnswer.value = answerKey;
        socket.send(
            JSON.stringify({
                action: 'submit_answer',
                quizId,
                answerKey,
                answerText
            })
        );
    }
}

const leftAnswers = computed(() => currentQuestion.value?.answers?.slice(0, 2) || []);
const rightAnswers = computed(() => currentQuestion.value?.answers?.slice(2, 4) || []);

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
    background-color: #3f6182;
    padding: 10px;
    border-radius: 5px;
    color: white;
    width: auto;
}

.timer-card {
    position: absolute;
    top: 10px;
    right: 10px;
    background-color: #3f6182;
    color: white;
    padding: 10px;
    border-radius: 5px;
    display: flex;
    align-items: center;
    justify-content: center;
    width: auto;
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
    background-color: #3f6182;
    width: 100%;
    padding: 16px;
    cursor: pointer;
    text-align: center;
}

.card-question {
    background-color: #3f6182;
    width: 100%;
    padding: 16px;
    text-align: center;
}

.card-spacing {
    margin-top: 10px;
    margin-bottom: 10px;
}

.correct-answer {
    background-color: #4caf50 !important;
    color: white;
}

.wrong-answer {
    background-color: #f44336 !important;
    color: white;
}

@media (min-width: 768px) {
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
}
</style>