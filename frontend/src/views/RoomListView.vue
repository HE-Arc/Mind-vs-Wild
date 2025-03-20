<template>
  <q-page class="q-pa-md">
    <div v-if="rooms.length">
      <h2>Rooms publiques</h2>
      <q-list bordered separator>
        <q-item v-for="room in publicRooms" :key="room.id" clickable @click="joinRoom(room.id)">
          <q-item-section>
            <div>{{ room.name }}</div>
            <div class="text-subtitle2 text-grey">Créé le: {{ new Date(room.created_at).toLocaleDateString() }}</div>
            <div class="text-subtitle2 text-grey">Participants: {{ room.participants.length }}</div>
          </q-item-section>
        </q-item>
      </q-list>
      <h2>Rooms de groupes</h2>
      <q-list bordered separator>
        <q-item v-for="room in groupRooms" :key="room.id" clickable @click="joinRoom(room.id)">
          <q-item-section>
            <div>{{ room.name }}</div>
            <div class="text-subtitle2 text-grey">Créé le: {{ new Date(room.created_at).toLocaleDateString() }}</div>
            <div class="text-subtitle2 text-grey">Participants: {{ room.participants.length }}</div>
          </q-item-section>
        </q-item>
      </q-list>
    </div>
    <div v-else class="text-center q-mt-md">
      <p>Aucune room disponible</p>
    </div>
    <q-btn label="Créer une Room" color="primary" class="q-mt-md" @click="createPublicRoom" />
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
    router.push(`/rooms/${room.id}`)
  }
}

const joinRoom = async (id) => {
  try {
    const response = await roomStore.joinRoom(id)
    const room = response.room
    router.push({
      path: `/rooms/${room.id}`,
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
