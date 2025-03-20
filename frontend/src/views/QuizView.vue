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