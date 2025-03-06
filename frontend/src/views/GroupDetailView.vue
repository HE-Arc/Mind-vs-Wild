<template>
  <q-page class="q-pa-md">

    <div class="text-center q-mb-md">
      <h2 class="text-h5 text-white text-bold q-ma-none">Détails du Groupe</h2>
      <div class="text-subtitle2 text-grey-7">{{ group.name }}</div>
    </div>
    <q-card bordered class="q-pa-md q-mb-md">
      <q-card-section>
        <div class="text-subtitle1 text-primary q-mb-xs">Infos du Groupe</div>
        <div class="q-mb-sm">
          <strong class="text-black">Description:</strong> <span class="text-black">{{ group.description }}</span>
        </div>
        <div class="q-mb-sm">
            <strong class="text-black">Créé par:</strong> <span class="text-black">{{ group.created_by }}</span>
        </div>
        <div class="q-mb-md">
          <strong class="text-black">Membres ({{ group.members?.length || 0 }}):</strong>
        </div>

        <q-list bordered separator class="rounded-borders q-mb-sm">
          <q-item v-for="member in group.members || []" :key="member.user.id" > 
            <q-item-section avatar>
              <q-avatar icon="person" color="primary" />
            </q-item-section>
            <q-item-section class="text-black">{{ member.user.username }}</q-item-section>
          </q-item>
        </q-list>
      </q-card-section>

      <q-card-actions align="right" class="q-pt-none">
        <q-btn label="Quitter le groupe" color="negative" icon="logout" @click="confirmLeaveGroup" />
      </q-card-actions>
    </q-card>

    <div v-if="isAdmin">
      <q-card bordered class="q-pa-md q-mb-md">
        <q-card-section>
          <div class="text-subtitle1 text-primary q-mb-md">Invitations</div>

          <div class="q-mb-md">
            <q-icon name="info" size="xs" color="grey-7" class="q-mr-sm" />
            <strong class="text-black">Invitation Générique :</strong>
          </div>
          <q-btn label="Générer un lien" color="secondary" @click="generateLink" />
          <div v-if="inviteLink" class="q-mt-sm">
            <q-input v-model="inviteLink" label="Lien généré" readonly outlined />
            <q-btn label="Copier" color="primary" icon="content_copy" @click="copyLink" class="q-mt-sm" />
          </div>

          <q-separator spaced />

          <div class="q-mb-md">
            <q-icon name="info" size="xs" color="grey-7" class="q-mr-sm" />
            <strong class="text-black">Invitation Nominative :</strong>
          </div>
          <q-input v-model="inviteUsername" label="Nom d'utilisateur" outlined dense />
          <q-btn label="Inviter" color="primary" @click="sendInvite" class="q-mt-sm" />
        </q-card-section>
      </q-card>
    </div>

    <q-card bordered class="q-pa-md">
      <q-card-section>
        <div class="text-subtitle1 text-primary q-mb-md">Rooms du Groupe</div>
        <q-list bordered separator>
          <q-item v-for="room in group.rooms" :key="room.id" clickable @click="goToRoom(room)">
            <q-item-section>
              <div class="text-bold">{{ room.name }}</div>
              <div class="text-subtitle2 text-grey">Code: {{ room.code }}</div>
            </q-item-section>
            <q-item-section side>
              <q-icon name="arrow_forward" />
            </q-item-section>
          </q-item>
        </q-list>
      </q-card-section>
    </q-card>

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

// Local state
const group = ref({})
const inviteUsername = ref('')
const inviteLink = ref('')
const confirmDialog = ref(false)

onMounted(async () => {
  await authStore.restoreUser()
  await groupStore.fetchGroups()
  const id = route.params.id
  group.value = groupStore.groups.find(g => g.id == id)
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

// Redirection vers une room
// function goToRoom(room) {
//   router.push(`/rooms/${room.code}`)
// }
// </script>
