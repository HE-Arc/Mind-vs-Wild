<template>
  <q-page class="q-pa-md">
    <div class="text-center q-mb-md">
      <h2 class="text-h5 text-white text-bold q-ma-none">{{ group.name }}</h2>
      <div class="text-subtitle2 text-grey-3">
        {{ group.description }}
      </div>
    </div>

    <div class="row q-col-gutter-md">
      <div class="col-12 col-md-4">
        <q-card bordered class="q-pa-md text-white">
          <q-card-section class="q-card-section">
            <div class="text-subtitle1 q-mb-xs">Infos du Groupe</div>
            <div class="q-mb-md">
              <strong>Membres ({{ group.members?.length || 0 }}):</strong>
            </div>

            <q-list class="rounded-borders q-mb-sm">
              <q-item v-for="member in group.members || []" :key="member.user.id">
                <q-avatar>
                  <img :src="member.user.avatar_url" :alt="member.user.username" />
                </q-avatar>
                <q-item-section>
                  <div class="row items-center">
                    {{ member.user.username }}
                    <q-icon v-if="member.user.id === group.created_by.id" name="star" color="amber-6" size="xs"
                      class="q-ml-xs" />
                  </div>
                </q-item-section>
              </q-item>
            </q-list>

            <q-card-actions align="right" class="q-pt-none">
              <q-btn label="Quitter le groupe" color="negative" icon="logout" @click="confirmLeaveGroup" />
            </q-card-actions>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-12 col-md-8">
        <div v-if="isAdmin">
          <q-card bordered class="q-pa-md q-mb-md text-white">
            <q-card-section class="q-card-section">
              <div class="text-subtitle1 q-mb-md">Invitations</div>

              <div class="q-mb-md">
                <q-icon name="info" size="xs" color="grey-7" class="q-mr-sm">
                  <q-tooltip>
                    Générer un lien d'invitation utilisable par n'importe qui. Une fois utilisé par un utilisateur, ce lien devient invalide.
                  </q-tooltip>
                </q-icon>
                <strong>Invitation Générique :</strong>
              </div>
              <q-btn label="Générer un lien" color="primary" @click="generateLink" />
              <div v-if="inviteLink" class="q-mt-sm">
                <q-input v-model="inviteLink" label="Lien généré" bg-color="white" outlined />
                <q-btn label="Copier" color="primary" icon="content_copy" @click="copyLink" class="q-mt-sm" />
              </div>

              <q-separator spaced />

              <div class="q-mb-md">
                <q-icon name="info" size="xs" color="grey-7" class="q-mr-sm">
                  <q-tooltip>
                    Générer un lien d'invitation utilisable uniquement par l'utilisateur spécifié dans le champs. Une fois utilisé ce lien devient invalide.
                  </q-tooltip>
                </q-icon>
                <strong>Invitation Nominative :</strong>
              </div>
              <q-input v-model="inviteUsername" label="Nom d'utilisateur" bg-color="white" outlined dense />
              <q-btn label="Inviter" color="primary" @click="sendInvite" class="q-mt-sm" />
            </q-card-section>
          </q-card>

          <q-card bordered class="q-pa-md q-mb-md text-white">
            <q-card-section class="q-card-section">
              <div class="text-subtitle1 q-mb-md">Créer une Room</div>
              <q-input v-model="newRoomName" label="Nom de la Room" bg-color="white" outlined dense />
              <q-btn label="Créer" color="primary" @click="createRoom" class="q-mt-sm" />
            </q-card-section>
          </q-card>
        </div>

        <q-card bordered class="q-pa-md q-mb-md ">
          <q-card-section class="q-card-section text-white">
            <div class="text-subtitle1 q-mb-md">Rooms du Groupe</div>
            <q-list bordered separator>
              <q-item v-for="room in group.rooms" :key="room.id" clickable @click="goToRoom(room)">
                <q-item-section>
                  <div class="text-bold">{{ room.name }}</div>
                  <div class="text-subtitle2 text-white">Participants: {{ room.participants.length }}</div>
                  <div class="text-subtitle2 text-white">Créé le: {{ new Date(room.created_at).toLocaleDateString() }}
                  </div>
                </q-item-section>
                <q-item-section side>
                  <q-icon name="arrow_forward" />
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <q-dialog v-model="confirmDialog">
      <q-card>
        <q-card-section>
          <div class="text-h6">Confirmer</div>
        </q-card-section>
        <q-card-section class="q-pt-none">
          Êtes-vous sûr de vouloir quitter ce groupe ?
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Annuler" v-close-popup />
          <q-btn flat label="Quitter" color="negative" @click="leaveGroup" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { copyToClipboard, useQuasar, Notify } from 'quasar'
import { useAuthStore } from '@/stores/useAuthStore'
import { useGroupStore } from '@/stores/group'
import { useRoomStore } from '@/stores/room'

const $q = useQuasar()
Notify.setDefaults({
  position: 'top',
  timeout: 3000,
  textColor: 'white',
  actions: [{ icon: 'close', color: 'white' }]
})

// Store instances
const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const groupStore = useGroupStore()
const roomStore = useRoomStore()

// Local state
const group = ref({})
const inviteUsername = ref('')
const inviteLink = ref('')
const confirmDialog = ref(false)
const newRoomName = ref('')

onMounted(async () => {
  await authStore.restoreUser()
  await groupStore.fetchGroups()
  const id = route.params.id
  group.value = groupStore.groups.find(g => g.id == id)
  if (group.value) {
    await roomStore.fetchRooms()
    group.value.rooms = roomStore.rooms.filter(room => room.group === group.value.id)
  }
})

const isAdmin = computed(() => {
  const user = authStore.user
  return user && group.value?.members?.some(m => m.user.id === user.id && m.is_admin)
})

function confirmLeaveGroup() {
  confirmDialog.value = true
}

async function leaveGroup() {
  try {
    await groupStore.leaveGroup(group.value.id)
    $q.notify({ type: 'positive', message: 'Vous avez quitté le groupe' })
    router.push('/groups')
  } catch (err) {
    $q.notify({ type: 'negative', message: err?.response?.data?.detail || 'Erreur' })
  }
}

async function sendInvite() {
  if (!inviteUsername.value) {
    $q.notify({ type: 'warning', message: 'Veuillez entrer un username' })
    return
  }
  try {
    const data = await groupStore.inviteUser(group.value.id, inviteUsername.value)
    inviteLink.value = data.invite_url
    $q.notify({ type: 'positive', message: 'Invitation créée' })
  } catch (err) {
    $q.notify({ type: 'negative', message: err?.response?.data?.detail || 'Erreur' })
  }
}

async function generateLink() {
  try {
    const data = await groupStore.inviteUser(group.value.id, null)
    inviteLink.value = data.invite_url
    $q.notify({ type: 'positive', message: 'Lien généré' })
  } catch (err) {
    $q.notify({ type: 'negative', message: err?.response?.data?.detail || 'Erreur' })
  }
}

function copyLink() {
  if (inviteLink.value) {
    copyToClipboard(inviteLink.value)
    $q.notify({ type: 'info', message: 'Lien copié !' })
  }
}

async function createRoom() {
  if (!newRoomName.value) {
    $q.notify({ type: 'warning', message: 'Veuillez entrer un nom de room' })
    return
  }
  try {
    const room = await roomStore.createRoom(newRoomName.value, group.value.id)
    $q.notify({ type: 'positive', message: 'Room créée' })
    router.push(`/rooms/${room.id}`)
  } catch (err) {
    $q.notify({ type: 'negative', message: err?.response?.data?.detail || 'Erreur' })
  }
}

function goToRoom(room) {
  router.push(`/rooms/${room.id}`)
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