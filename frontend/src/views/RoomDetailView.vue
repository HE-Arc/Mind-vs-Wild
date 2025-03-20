<template>
  <q-page class="q-pa-md">
    <div v-if="room">
      <div class="text-center q-mb-md">
        <h2 class="text-h5 text-white text-bold q-ma-none">{{ room.name }}</h2>
        <div class="text-subtitle2 text-grey-7">Code: {{ room.code }}</div>
      </div>
      <h3>Participants ({{ room.participants.length }})</h3>
      <ul>
        <li v-for="p in room.participants" :key="p.id">{{ p.user.username }}</li>
      </ul>
  
      <q-btn color="negative" label="Quitter la Room" class="q-mt-md" @click="leaveRoom" />
    </div>

    <div v-else class="text-center q-mt-md">
      <q-spinner size="50px" color="primary" />
      <p>Loading room details...</p>
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRoomStore } from '@/stores/room'
import { useQuasar } from 'quasar'

const route = useRoute()
const router = useRouter()
const roomStore = useRoomStore()
const $q = useQuasar()

const room = ref(null)
const message = ref(route.query.message || '')

onMounted(async () => {
  const code = route.params.code
  room.value = await roomStore.fetchRoomDetails(code)
  if(message.value) {
    $q.notify({ type: 'positive', message: message.value })
  }
})

const leaveRoom = async () => {
  await roomStore.leaveRoom()
  router.push('/rooms')
}
</script>
