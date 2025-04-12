<template>
    <q-page class="q-page">
        <q-card v-if="currentQuestion" class="question-card">
            <q-card-section class="q-pa-none card-question">
                {{ currentQuestion.text }}
            </q-card-section>
        </q-card>

        <q-card class="timer-card">
            <q-card-section class="q-pa-none timer-text">
                <q-icon name="hourglass_empty" class="timer-icon" />
                {{ formatTime(timeLeft) }}
            </q-card-section>
        </q-card>

        <div v-if="!isPlayerActive" class="result-message eliminated">
            <span>Vous êtes éliminé.</span>
        </div>
        
        <div v-if="lastResult" class="result-message"
            :class="{ 
                'correct': lastResult === 'correct', 
                'incorrect': lastResult === 'incorrect' 
            }">
            <span v-if="lastResult === 'correct'">Bonne réponse !</span>
            <span v-else>Réponse incorrecte. La bonne réponse était {{ correctAnswer }}.</span>
        </div>

        <div v-if="currentQuestion" class="answer">
            <div class="column left-column">
                <q-card v-for="answer in leftAnswers" class="card-spacing" :class="{
                    'correct-answer': lastResult === 'correct' && answer === selectedAnswer,
                    'wrong-answer': lastResult === 'incorrect' && answer === selectedAnswer
                }" @click="onAnswerClick(currentQuestion.id, answer)">
                    <q-card-section class="q-pa-none card-answer">
                        {{ answer }}
                    </q-card-section>
                </q-card>
            </div>
            <div class="column right-column">
                <q-card v-for="answer in rightAnswers" class="card-spacing" :class="{
                    'correct-answer': lastResult === 'correct' && answer === selectedAnswer,
                    'wrong-answer': lastResult === 'incorrect' && answer === selectedAnswer
                }" @click="onAnswerClick(currentQuestion.id, answer)">
                    <q-card-section class="q-pa-none card-answer">
                        {{ answer }}
                    </q-card-section>
                </q-card>
            </div>
        </div>
    </q-page>
</template>

<script setup>
import { computed } from 'vue';

// Props
const props = defineProps({
    currentQuestion: {
        type: Object,
        default: null
    },
    timeLeft: {
        type: Number,
        default: 0
    },
    maxTime: {
        type: Number,
        default: 30
    },
    lastResult: {
        type: String,
        default: null
    },
    correctAnswer: {
        type: String,
        default: null
    },
    selectedAnswer: {
        type: String,
        default: null
    },
     isPlayerActive: {
         type: Boolean,
         default: true
    }
});

// Emits
const emit = defineEmits(['submit-answer']);

// Computed properties
const leftAnswers = computed(() => props.currentQuestion?.options?.slice(0, 2) || []);
const rightAnswers = computed(() => props.currentQuestion?.options?.slice(2, 4) || []);

// Methods
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

function onAnswerClick(questionId, answer) {
    if (!props.isPlayerActive || props.selectedAnswer !== null) return; 
    emit('submit-answer', questionId, answer);
}
</script>

<style scoped>
.q-page {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 20px;
    position: relative;
}

.question-card {
    width: 100%;
    max-width: 800px;
    margin-bottom: 20px;
}

.timer-card {
    background-color: #3f6182;
    color: white;
    padding: 10px 20px;
    border-radius: 5px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.timer-text {
    font-size: 1.5rem;
    display: flex;
    align-items: center;
    gap: 10px;
}

.timer-icon {
    font-size: 1.5rem;
}

.answer {
    display: flex;
    flex-direction: column;
    gap: 20px;
    width: 100%;
    max-width: 800px;
}

.column {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.card-answer {
    background-color: #3f6182;
    color: white;
    padding: 16px;
    cursor: pointer;
    text-align: center;
    transition: all 0.2s ease;
    
    &:hover {
        box-shadow: 0 0 10px 2px #EE7154;
    }
}

.card-question {
    background-color: #3f6182;
    color: white;
    padding: 20px;
    text-align: center;
    font-size: 1.2rem;
}

.result-message {
    margin: 20px 0;
    padding: 15px;
    border-radius: 5px;
    text-align: center;
    font-weight: bold;
    
    &.correct {
        background-color: #4caf50;
        color: white;
    }
    
    &.incorrect {
        background-color: #f44336;
        color: white;
    }
}

.result-message.eliminated {
    background-color: #9e9e9e;
    color: white;
    margin: 20px 0;
    padding: 15px;
    border-radius: 5px;
    text-align: center;
    font-weight: bold;
}

.correct-answer {
    background-color: #4caf50 !important;
}

.wrong-answer {
    background-color: #f44336 !important;
}

@media (min-width: 768px) {
    .answer {
        flex-direction: row;
    }
}
</style>