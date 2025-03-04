<template>
  <q-page class="q-pa-md">
    <h2>Rejoindre une Room</h2>
    <q-input v-model="code" label="Code de la Room" outlined dense @keyup.enter="joinRoom" />
    <q-btn label="Rejoindre" color="primary" class="q-mt-md" @click="joinRoom" />

    <q-banner v-if="message" class="q-mt-md"
      :class="{ 'bg-positive text-white': success, 'bg-negative text-white': !success }">
      {{ message }}
    </q-banner>
  </q-page>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useRoomStore } from '@/stores/room'

const router = useRouter()
const roomStore = useRoomStore()

const code = ref('')
const message = ref('')
const success = ref(false)

const joinRoom = async () => {
  if (!code.value) {
    message.value = "Veuillez entrer un code de room."
    success.value = false
    return
  }
  try {
    const room = await roomStore.joinRoomByCode(code.value)
    message.value = `Vous avez rejoint la room : ${room.name}`
    success.value = true
    setTimeout(() => {
      router.push(`/rooms/${room.code}`)
    }, 1000)
  } catch (error) {
    console.error("Erreur lors de la jointure :", error)
    message.value = "Impossible de rejoindre cette room."
    success.value = false
  }
}
</script>
