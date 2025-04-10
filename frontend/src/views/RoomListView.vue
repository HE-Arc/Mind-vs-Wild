<template>
  <q-page class="q-pa-md">
    <div class="row items-center justify-between q-mb-md">
      <h2 class="q-ma-none text-white">Liste des Rooms</h2>
      <q-btn 
        color="primary" 
        icon="add" 
        label="Créer une Room" 
        @click="showCreateModal = true"
      />
    </div>

    <div class="row">
      <div class="col-12">
        <div v-if="rooms.length">
          <h2 class="text-white">Rooms publiques</h2>
          <div class="row q-col-gutter-md q-mt-xs">
            <div v-for="room in publicRooms" :key="room.id" class="col-12 col-sm-6">
              <q-card class="cursor-pointer text-white q-card" @click="joinRoom(room.id)">
                <q-card-section class="q-card-section ">
                  <div class="text-h6">{{ room.name }}</div>
                  <div class="text-subtitle2">Créé le: {{ new Date(room.created_at).toLocaleDateString() }}</div>
                  <div class="text-subtitle2">
                    <q-icon name="people" /> {{ room.participants.length }} participants
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </div>

          <h2 class="q-mt-lg text-white">Rooms de groupes</h2>
          <div class="row q-col-gutter-md q-mt-xs">
            <div v-for="room in groupRooms" :key="room.id" class="col-12 col-sm-6">
              <q-card class="cursor-pointer q-card text-white" @click="joinRoom(room.id)">
                <q-card-section class="q-card-section ">
                  <div class="text-h6">{{ room.name }}</div>
                  <div class="text-subtitle2">Créé le: {{ new Date(room.created_at).toLocaleDateString() }}</div>
                  <div class="text-subtitle2">
                    <q-icon name="people" /> {{ room.participants.length }} participants
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </div>
        <div v-else class="text-center q-mt-md">
          <p>Aucune room disponible</p>
        </div>
      </div>
    </div>

    <q-dialog v-model="showCreateModal">
      <q-card style="width: 500px; max-width: 90vw;">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Créer une Room publique</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-form @submit.prevent="createPublicRoom">
          <q-card-section>
            <q-input 
              v-model="newRoomName" 
              label="Nom de la Room" 
              outlined 
              :placeholder="`Room de ${username}`"
              class="q-mb-md"
              bg-color="white"
            />
          </q-card-section>

          <q-card-actions align="right">
            <q-btn label="Annuler" flat v-close-popup />
            <q-btn label="Créer" color="primary" type="submit" />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoomStore } from '@/stores/room'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'

const roomStore = useRoomStore()
const router = useRouter()
const rooms = ref([])
const message = ref('')
const $q = useQuasar()
const showCreateModal = ref(false)

onMounted(async () => {
  await roomStore.fetchRooms()
  rooms.value = roomStore.rooms
})

const publicRooms = computed(() => rooms.value.filter(room => !room.group))
const groupRooms = computed(() => rooms.value.filter(room => room.group))

const username = computed(() => {
  const authStore = useAuthStore()
  return authStore.user ? authStore.user.username : ''
})

const newRoomName = ref('')

const createPublicRoom = async () => {
  const roomName = newRoomName.value || `Room de ${username.value}`
  const room = await roomStore.createRoom(roomName)
  showCreateModal.value = false
  router.push(`/rooms/${room.id}`)
  newRoomName.value = ''
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

<style scoped>
.q-card {
  background-color: #2c2c38;
}

.q-card-section {
  background-color: #2c2c38;
}
</style>