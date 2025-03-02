  <template>
    <q-page class="q-pa-md">
      <h2>Détails du Groupe</h2>
      <q-card class="q-mb-md">
        <q-card-section color="primary" class="text-white">
          <div class="text-h6">{{ group.name }}</div>
          <div class="text-subtitle2">Description : {{ group.description }}</div>
          <div>Créé par : {{ group.created_by }}</div>
        </q-card-section>
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
import { copyToClipboard, useQuasar } from 'quasar'

import { useAuthStore } from '@/stores/useAuthStore'
import { useGroupStore } from '@/stores/group'

const $q = useQuasar()
const route = useRoute()
const router = useRouter()

// On récupère les stores
const authStore = useAuthStore()
const groupStore = useGroupStore()

// Données locales
const group = ref({})
const inviteUsername = ref('')
const inviteLink = ref('')

// Rediriger vers la room
const goToRoom = (room) => {
  router.push(`/room/${room.id}`)
}

onMounted(async () => {
  await authStore.restoreUser()

  await groupStore.fetchGroups()

  const id = route.params.id
  group.value = groupStore.groups.find(g => g.id == id)
})

const isAdmin = computed(() => {
  const user = authStore.user
  if (!user) return false

  // On check si la liste members est prête

  return group.value.members?.some(m => m.user.id === user.id && m.is_admin)

})

// *** Fonctions invitation ***
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
</script>
