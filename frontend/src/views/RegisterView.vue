<template>
    <q-layout>
      <q-page-container>
        <q-form @submit="register" @reset="reset" class="q-gutter-md">
          <q-input v-model="firstName" label="Prénom*" required outlined />
          <q-input v-model="lastName" label="Nom*" required outlined />
          <q-input v-model="email" label="Adresse email*" required outlined />
          <q-input v-model="username" label="Nom d'utilisateur*" required outlined />
          <q-input v-model="password" label="Mot de passe*" type="password" required outlined class="q-mt-md" />
          <q-btn label="S'inscrire" type="submit" color="primary" class="full-width q-mt-md" />
        </q-form>
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
      const errorMessage = ref('')
  
      const register = async () => {
        try {
          const response = await axios.post('http://127.0.0.1:8000/api/auth/register/', {
            first_name: firstName.value,
            last_name: lastName.value,
            email: email.value,
            username: username.value,
            password: password.value
          })
  
          console.log(response.data)
        } catch (error) {
          errorMessage.value = error.response?.data?.error || "Unknown error"
          console.error(errorMessage.value)
        }
      }
  
      return { firstName, lastName, email, username, password, register, errorMessage }
    }
  }
  </script>
  