<template>
  <q-layout>
    <q-page-container>
      <q-page class="flex flex-column flex-center justify-center">
        <div class="flex flex-column items-center ">
          <q-img src="/logo.png" class="q-mb-md q-mx-auto logo-img" />
          <q-form @submit="register" @reset="reset" class="q-gutter-md full-width q-form">
            <q-input rounded standout bg-color="white" color="black" input-style="color: black;" v-model="email"
              label="Adresse email*" class="full-width" required outlined />
            <q-input rounded standout bg-color="white" color="black" input-style="color: black;" v-model="username"
              label="Nom d'utilisateur*" class="full-width" required outlined />
            <q-input rounded standout bg-color="white" color="black" input-style="color: black;" v-model="password"
              label="Mot de passe*" type="password" required outlined class="full-width" />
            <q-btn rounded label="S'inscrire" type="submit" class="full-width btn" />
          </q-form>
        </div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script>
import { ref } from 'vue'
import axios from 'axios'

export default {
  setup() {
    const firstName = ref('')
    const lastName = ref('')
    const email = ref('')
    const username = ref('')
    const password = ref('')
    const confirmPassword = ref('')
    const errorMessage = ref('')

    const register = async () => {
      try {
        const response = await axios.post('http://127.0.0.1:8000/api/auth/register/', {
          username: username.value,
          password: password.value,
          email: email.value,
        })

        console.log(response.data)
      } catch (error) {
        errorMessage.value = error.response?.data?.error || "Unknown error"
        console.error(errorMessage.value)
      }
    }

    return { firstName, lastName, email, username, password, confirmPassword, register, errorMessage }
  }
}
</script>

<style scoped>
.btn {
  margin-top: 1rem;
  background-color: #EE7154;
  color: white;
}

.logo-img {
  max-width: 200px;
  max-height: 200px;
  border-radius: 50%;
}

.q-form {
  max-width: 800px;
  width: 100%;
}

.q-input {
  font-size: 1.2rem;
  min-height: 56px;
}
</style>
