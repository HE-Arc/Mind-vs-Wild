<template>
  <q-page class="flex flex-center justify-center ">
    <div class="flex flex-column items-center">
      <q-img src="/logo.png" class="q-mb-md q-mx-auto logo-img" />
      <q-input rounded standout v-model="username" label="Nom d'utilisateur" bg-color="white" color="black"
        input-style="color: black;" class="full-width " />
      <q-input rounded standout v-model="password" label="Mot de passe" type="password" bg-color="white" color="black"
        input-style="color: black;" class="q-mt-md full-width" />
      <q-btn rounded label="Se connecter" class="full-width q-mt-md btn" @click="login" />
      <q-card-section v-if="errorMessage" class="text-negative">
        {{ errorMessage }}
      </q-card-section>
      <router-link to="/register" class="q-mt-md">Pas de compte ? S'inscrire</router-link>
    </div>
  </q-page>
</template>

<script>
import { defineComponent, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/useAuthStore'

export default defineComponent({
  name: 'LoginView',
  setup() {
    const username = ref('')
    const password = ref('')
    const errorMessage = ref('')
    const router = useRouter()
    const authStore = useAuthStore()

    const login = async () => {
      const success = await authStore.login(username.value, password.value)

      if (success) {
        await authStore.restoreUser() // Get user info
        router.push('/profile') // Redirection
      } else {
        errorMessage.value = 'Échec de la connexion. Vérifiez vos informations.'
      }
    }

    return { username, password, login, errorMessage }
  }
});
</script>

<style scoped>
.btn {
  margin-top: 1rem;
  background-color: #EE7154;
  color: white;
}

.logo-img {
  max-width: 300px;
  max-height: 300px;
  border-radius: 50%;
}
</style>
