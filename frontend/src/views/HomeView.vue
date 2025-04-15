<template>
  <main class="main-container">
    <QCard class="my-card">
      <QCardSection>
        <h1 class="title text-black">Bienvenue sur <strong>Mind vs Wild</strong> !</h1>
        <h2 class="subtitle text-black">Ton esprit contre tous les autres... Qui survivra à la jungle du savoir ?</h2>
        <p class="text-black"><strong>Mind vs Wild</strong>, c’est le jeu de quiz en mode battle royale : une seule règle, ne jamais se
          tromper.</p>
        <p class="text-black">À chaque mauvaise réponse, c’est l’élimination. Seul le dernier en lice remporte la victoire.</p>
        <p class="cta text-black">Prêt à tester tes connaissances et affronter les autres joueurs ?</p>
      </QCardSection>

      <QCardActions class="btn-group">
        <template v-if="!isLoggedIn">
          <QBtn to="/register" color="primary" label="S'enregistrer" />
          <QBtn to="/login" color="primary" label="Se connecter" />
        </template>
        <template v-else>
          <QBtn to="/profile" color="primary" label="Mon profil" />
          <QBtn to="/rooms" color="primary" label="Rejoindre une partie" />
        </template>
      </QCardActions>
    </QCard>
  </main>
</template>

<script setup lang="ts">
import { QCard, QCardSection, QCardActions, QBtn } from 'quasar'
import { useAuthStore } from '@/stores/auth'
import { computed } from 'vue'

const authStore = useAuthStore()
const isLoggedIn = computed(() => authStore.isLoggedIn)
</script>

<style scoped>
.main-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 16px;
  min-height: calc(100vh - 98px - 50px); 
  background: linear-gradient(135deg, #1b1f24, #2a2f36);
  box-sizing: border-box;
}

.my-card {
  width: 100%;
  max-width: 700px;
  background-color: #ffffff;
  border: 4px solid #EE7154;
  border-radius: 16px;
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.2);
  padding: 24px;
  box-sizing: border-box;
  margin: auto;
}

.title {
  font-size: 2rem;
  margin-bottom: 12px;
}

.subtitle {
  font-size: 1.2rem;
  color: #444;
  margin-bottom: 20px;
}

.cta {
  margin-top: 20px;
  font-weight: bold;
}

.btn-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: flex-end;
  padding: 0 16px 16px;
}

@media (max-width: 600px) {
  .my-card {
    padding: 16px;
  }

  .btn-group {
    flex-direction: column;
    align-items: stretch;
  }

  .title {
    font-size: 1.6rem;
  }

  .subtitle {
    font-size: 1rem;
  }
}
</style>
