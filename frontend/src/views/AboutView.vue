<template>
  <main class="main-container">
    <QCard class="my-card">
      <QCardSection>
        <h1 class="title text-black">À propos de <strong>Mind vs Wild</strong></h1>
        <p class="text-black"><strong>Mind vs Wild</strong> est une expérience unique de quiz en mode battle royale. Notre mission est de te défier, de te divertir et de te pousser à repousser les limites de tes connaissances.</p>
        <p class="text-black">Rejoins une communauté de joueurs passionnés et découvre qui est le plus grand survivant dans la jungle du savoir.</p>
        <p class="cta text-black">Prêt à relever le défi ?</p>
        <p class="text-black">Cette application web est un projet réalisé dans le cadre de la formation d'ingénierie en infornatique logicielle au sein de la HE-ARC</p>
        <p class="text-black">Il s'agit d'un projet réalisé par : </p>
        <ul class="text-black">
          <li>Jaton David</li>
          <li>Magnin Nicolas</li>
          <li>Vivone Tom</li>
        </ul>
        <p class="text-black">Pour la réalisation du site a été utilisé : </p>
        <ul class="text-black">
          <li>Django</li>
          <li>Vue.js</li>
          <li>Quasar</li>
        </ul>

      </QCardSection>

      <QCardActions class="btn-group">
        <QBtn :to="'/'" color="primary" label="Retour à l'accueil" />
      </QCardActions>
    </QCard>
  </main>
</template>

<script setup lang="ts">
import { QCard, QCardSection, QCardActions, QBtn } from 'quasar'
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
}
</style>
