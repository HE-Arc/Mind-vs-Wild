<template>
  <q-page class="q-pa-md">
    <h2>Rooms Disponibles</h2>
    <q-list bordered separator>
      <q-item v-for="room in rooms" :key="room.id" clickable @click="joinRoom(room)">
        <q-item-section>
          <div>{{ room.name }}</div>
          <div class="text-subtitle2 text-grey">Code : {{ room.code }}</div>
        </q-item-section>
      </q-item>
    </q-list>

    <h3 class="q-mt-md">Rejoindre une Room</h3>
    <q-input v-model="joinCode" label="Code de la Room" outlined dense @keyup.enter="joinRoomByCode" />
    <q-btn label="Rejoindre" color="primary" class="q-mt-md" @click="joinRoomByCode" />

    <q-banner v-if="message" class="q-mt-md"
      :class="{ 'bg-positive text-white': success, 'bg-negative text-white': !success }">
      {{ message }}
    </q-banner>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoomStore } from '@/stores/room'
import { useRouter } from 'vue-router'

const roomStore = useRoomStore()
const router = useRouter()
const rooms = ref([])
const joinCode = ref('')
const message = ref('')
const success = ref(false)

onMounted(async () => {
  await roomStore.fetchRooms()
  rooms.value = roomStore.rooms
})

const joinRoomByCode = async () => {
  if (!joinCode.value) {
    message.value = "Veuillez entrer un code de room."
    success.value = false
    return
  }
  try {
    const room = await roomStore.joinRoomByCode(joinCode.value)
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

const joinRoom = (room) => {
  router.push(`/rooms/${room.code}`)
}
</script>
