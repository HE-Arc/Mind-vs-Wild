  <template>
    <q-page class="q-pa-md">
      <h2>Détails du Groupe</h2>
      <q-card class="q-mb-md">
        <q-card-section color="secondary" class="text-black">
          <div class="text-h6">{{ group.name }}</div>
          <div class="text-subtitle2">Description : {{ group.description }}</div>
          <div>Créé par : {{ group.created_by }}</div>
          <div>Membres :</div>
          <q-list bordered separator>
            <q-item v-for="member in group.members" :key="member.user.id">
              <q-item-section>
                <div>{{ member.user.username }}</div>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>
        <q-btn label="Quitter le groupe" color="negative" @click="leaveGroup" class="q-mt-md" />
      </q-card>
      <div v-if="isAdmin">
        <q-input v-model="inviteUsername" label="Nom d'utilisateur à inviter" outlined dense v-if="isAdmin" />
        <q-btn label="Inviter" color="primary" @click="sendInvite" class="q-mt-md" />
        <q-btn label="Générer Lien d'Invitation" color="secondary" @click="generateLink" class="q-ml-sm" />

        <div v-if="inviteLink" class="q-mt-md">
          <q-input v-model="inviteLink" label="Lien d'invitation" readonly outlined />
          <q-btn label="Copier" @click="copyLink" />
        </div>
      </div>
      <h3>Rooms du Groupe</h3>
      <q-list bordered separator>
        <q-item v-for="room in group.rooms" :key="room.id" clickable @click="goToRoom(room)">
          <q-item-section>
            <div>{{ room.name }}</div>
            <div class="text-subtitle2">Code : {{ room.code }}</div>
          </q-item-section>
        </q-item>
      </q-list>
    </q-page>
  </template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { copyToClipboard, useQuasar, Notify } from 'quasar'

import { useAuthStore } from '@/stores/useAuthStore'
import { useGroupStore } from '@/stores/group'

const $q = useQuasar()
Notify.setDefaults({
  position: 'top',
  timeout: 3000,
  textColor: 'white',
  actions: [{ icon: 'close', color: 'white' }]
})
const route = useRoute()
const router = useRouter()

// Stores
const authStore = useAuthStore()
const groupStore = useGroupStore()

// Local state
const group = ref({})
const inviteUsername = ref('')
const inviteLink = ref('')

// Redirect to room detail
// const goToRoom = (room) => {
//   router.push(`/room/${room.id}`)
// }

onMounted(async () => {
  await authStore.restoreUser()
  await groupStore.fetchGroups()

  const id = route.params.id
  group.value = groupStore.groups.find(g => g.id == id)
})

const isAdmin = computed(() => {
  const user = authStore.user
  console.log(group.value)
  if (!user) return false

  // Check if user is admin of the group
  return group.value?.members?.some(m => m.user.id === user.id && m.is_admin)

})

// Send invite
const sendInvite = async () => {
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

const generateLink = async () => {
  try {
    const data = await groupStore.inviteUser(group.value.id, null)
    inviteLink.value = data.invite_url
    $q.notify({ type: 'positive', message: 'Invitation (lien générique) créée' })
  } catch (err) {
    $q.notify({ type: 'negative', message: err?.response?.data?.detail || 'Erreur' })
  }
}

const copyLink = () => {
  if (!inviteLink.value) return
  copyToClipboard(inviteLink.value).then(() => {
    $q.notify({ type: 'info', message: 'Lien copié !' })
  })
}

const leaveGroup = async () => {
  try {
    await groupStore.leaveGroup(group.value.id)
    $q.notify({ type: 'positive', message: 'Vous avez quitté le groupe' })
    router.push('/groups')
  } catch (err) {
    $q.notify({ type: 'negative', message: err?.response?.data?.detail || 'Erreur' })
  }
}
</script>
