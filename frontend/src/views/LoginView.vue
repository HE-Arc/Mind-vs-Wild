<template>
    <q-layout>
        <q-page-container>
            <q-page class="flex flex-center justify-center ">
                <div class="flex flex-column items-center">
                    <q-img src="/logo.png" class="q-mb-md q-mx-auto logo-img"/>
                    <q-input rounded standout v-model="username" label="Nom d'utilisateur" bg-color="white" color="black" input-style="color: black;" class="full-width "/>
                    <q-input rounded standout v-model="password" label="Mot de passe" type="password" bg-color="white" color="black" input-style="color: black;" class="q-mt-md full-width"/>
                    <q-btn rounded label="Se connecter" class="full-width q-mt-md btn" @click="login" />
                    <q-card-section v-if="errorMessage" class="text-negative">
                        {{ errorMessage }}
                    </q-card-section>
                    <router-link to="/register" class="q-mt-md">Pas de compte ? S'inscrire</router-link>
                </div>
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
                const response = await axios.post(`${import.meta.env.VITE_BACKEND_URL}/api/auth/login/`, {
                    username: username.value,
                    password: password.value
                })

                const token = response.data.token
                localStorage.setItem('token', token)
                
                router.push('/profile')
            } catch (error) {
                errorMessage.value = error.response?.data?.error || "Unknow error"
            }
        }

        return { username, password, login, errorMessage }
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
    max-width: 300px;
    max-height: 300px;
    border-radius: 50%;
}
</style>
