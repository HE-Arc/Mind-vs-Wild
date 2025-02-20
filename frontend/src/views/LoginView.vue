<template>
    <q-layout>
        <q-page-container>
            <q-page class="flex flex-center">
                <q-card class="q-pa-md" style="width: 400px;">
                    <q-card-section>
                        <div class="text-h6">Connexion</div>
                    </q-card-section>

                    <q-card-section>
                        <q-input v-model="username" label="Nom d'utilisateur" outlined />
                        <q-input v-model="password" label="Mot de passe" type="password" outlined class="q-mt-md" />
                        <q-btn label="Se connecter" color="primary" class="full-width q-mt-md" @click="login" />
                        <router-link to="/register" class="q-mt-md">Pas de compte ? S'inscrire</router-link>

                    </q-card-section>

                    <q-card-section v-if="errorMessage" class="text-negative">
                        {{ errorMessage }}
                    </q-card-section>
                </q-card>
            </q-page>
        </q-page-container>
    </q-layout>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

export default {
    setup() {
        const username = ref('')
        const password = ref('')
        const errorMessage = ref('')
        const router = useRouter()

        const login = async () => {
            try {
                const response = await axios.post('http://127.0.0.1:8000/api/auth/login/', {
                    username: username.value,
                    password: password.value
                })
                console.log(response.data)
                router.push('/dashboard')
            } catch (error) {
                errorMessage.value = error.response?.data?.error || "Unknow error"
            }
        }

        return { username, password, login, errorMessage }
    }
}
</script>