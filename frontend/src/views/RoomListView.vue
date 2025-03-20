<template>
  <q-page class="q-pa-md">
    <div v-if="rooms.length">
      <h2>Rooms publiques</h2>
      <q-list bordered separator>
        <q-item v-for="room in publicRooms" :key="room.id" clickable @click="joinRoom(room.code)">
          <q-item-section>
            <div>{{ room.name }}</div>
            <div class="text-subtitle2 text-grey">Code : {{ room.code }}</div>
          </q-item-section>
        </q-item>
      </q-list>
      <h2>Rooms de groupes</h2>
      <q-list bordered separator>
        <q-item v-for="room in groupRooms" :key="room.id" clickable @click="joinRoom(room.code)">
          <q-item-section>
            <div>{{ room.name }}</div>
            <div class="text-subtitle2 text-grey">Code : {{ room.code }}</div>
          </q-item-section>
        </q-item>
      </q-list>
    </div>
    <div v-else class="text-center q-mt-md">
      <p>Aucune room disponible</p>
    </div>
    <q-btn label="Créer une Room" color="primary" class="q-mt-md" @click="createPublicRoom" />
    <h3 class="q-mt-md">Rejoindre une Room</h3>
    <q-input v-model="joinCode" label="Code de la Room" outlined dense @keyup.enter="joinRoom(joinCode)" />
    <q-btn label="Rejoindre" color="primary" class="q-mt-md" @click="joinRoom(joinCode)" />
  </q-page>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoomStore } from '@/stores/room'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'

const roomStore = useRoomStore()
const router = useRouter()
const rooms = ref([])
const joinCode = ref('')
const message = ref('')
const $q = useQuasar()

onMounted(async () => {
  await roomStore.fetchRooms()
  rooms.value = roomStore.rooms
})

const publicRooms = computed(() => rooms.value.filter(room => !room.group))
const groupRooms = computed(() => rooms.value.filter(room => room.group))

const createPublicRoom = async () => {
  const name = prompt('Enter room name:')
  if (name) {
    const room = await roomStore.createRoom(name)
    router.push(`/rooms/${room.code}`)
  }
}

const joinRoom = async (code) => {
  if (!code || code === '') {
    message.value = "Veuillez entrer un code de room."
    $q.notify({ type: 'negative', message: 'Veuillez entrer un code de room.' })
    return
  }
  try {
    const response = await roomStore.joinRoomByCode(code)
    const room = response.room
    router.push({
      path: `/rooms/${room.code}`,
      query: {
        message: response.detail,
      }
    })
  } catch (error) {
    console.error("Erreur lors de la jointure :", error)
    $q.notify({ type: 'negative', message: 'Impossible de rejoindre cette room.' })
  }
}
</script>
