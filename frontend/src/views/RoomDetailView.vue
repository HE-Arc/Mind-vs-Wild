<template>
  <div class="q-pa-md">
    <h2>{{ room.name }}</h2>
    <p>Code de la Room : {{ room.code }}</p>

    <h3>Participants ({{ room.participants.length }})</h3>
    <ul>
      <li v-for="p in room.participants" :key="p.id">{{ p.username }}</li>
    </ul>

    <q-btn color="negative" label="Quitter la Room" class="q-mt-md" @click="leaveRoom" />
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useRoomStore } from '@/stores/room'
import { useRoute, useRouter } from 'vue-router'

const roomStore = useRoomStore()
const route = useRoute()
const router = useRouter()

onMounted(() => {
  const code = route.params.code
  roomStore.fetchRoomDetails(code)
})

const room = computed(() => roomStore.currentRoom)

// TODO: Implement leaveRoom function
// const leaveRoom = () => {
//   $q.notify({ type: 'info', message: "La fonctionnalité 'Quitter' sera bientôt disponible" })
//   router.push('/rooms')
// }
</script>
