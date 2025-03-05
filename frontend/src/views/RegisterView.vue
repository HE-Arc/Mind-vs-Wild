<template>
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
</template>

<script>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'


export default {
  setup() {
    const firstName = ref('')
    const lastName = ref('')
    const email = ref('')
    const username = ref('')
    const password = ref('')
    const confirmPassword = ref('')
    const errorMessage = ref('')
    const router = useRouter()

    const register = async () => {
      try {
        const response = await axios.post(`${import.meta.env.VITE_BACKEND_URL}/api/auth/register/`, {
          username: username.value,
          password: password.value,
          email: email.value,
        }, {
          withCredentials: true
        });
        router.push('/login');
      } catch (error) {
        errorMessage.value = error.response?.data?.error || "Unknown error";
      }
    }

    return { email, username, password, register, errorMessage }
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
