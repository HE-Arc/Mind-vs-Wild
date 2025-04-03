<template>
  <q-layout view="hHh lpR fFf">
    <q-header reveal elevated class="bg-accent text-white standout q-pa-md">
      <q-toolbar>
        <q-toolbar-title>
          <q-avatar size="60px" class="q-mr-sm">
            <img src="/logo.png" alt="Mind vs Wild Logo" />
          </q-avatar>
        </q-toolbar-title>

        <q-btn dense flat to="/" label="Home" />
        <q-btn dense flat to="/rooms" label="Rooms" />
        <q-btn dense flat to="/about" label="About" />

        <q-btn dense flat round icon="menu" @click="toggleRightDrawer" />
      </q-toolbar>
    </q-header>

    <!-- Right Drawer -->
    <q-drawer show-if-above v-model="rightDrawerOpen" side="right" bordered>
      <q-list>
        <template v-if="!isLoggedIn">
          <q-item clickable to="/login" class="text-black">
            <q-item-section>Se connecter</q-item-section>
          </q-item>
          <q-item clickable to="/register" class="text-black">
            <q-item-section>S'enregistrer</q-item-section>
          </q-item>
        </template>
        <template v-else>
          <q-item clickable @click="goToProfile" class="text-black">
            <q-item-section avatar>
              <q-avatar>
                <img :src="authStore.user.avatar_url" :alt="authStore.user.username" />
              </q-avatar>
            </q-item-section>
            <q-item-section>
              <q-item-label>{{ authStore.user.username }}</q-item-label>
            </q-item-section>
          </q-item>
          <q-separator />
          <q-item class="text-black">
            <q-item-section>
              <q-item-label>Mes groupes : </q-item-label>
            </q-item-section>
          </q-item>
          <q-separator />
          <q-item>
            <q-item-section>
              <q-list bordered separator>
                <q-item v-for="group in groups" :key="group.id" clickable @click="goToGroupDetail(group.id)"
                  class="text-black">
                  <q-item-section>{{ group.name }}</q-item-section>
                </q-item>
              </q-list>
            </q-item-section>
          </q-item>
          <q-item class="text-black">
            <q-item-section>
              <q-btn label="Créer un groupe" @click="showCreateGroupModal = true" color="primary" />
            </q-item-section>
          </q-item>

        </template>
      </q-list>

      <q-dialog v-model="showCreateGroupModal">
        <q-card bordered class="q-pa-md">
          <q-card-section>
            <div class="text-subtitle1 text-primary q-mb-md">
              Créer un Nouveau Groupe
            </div>

            <q-input v-model="newGroupName" label="Nom du groupe" outlined class="q-mb-md" maxlength="35" counter />
            <q-input v-model="newGroupDesc" label="Description" type="textarea" outlined class="q-mb-md" maxlength="256" counter />

            <q-btn label="Créer Groupe" color="primary" @click="createGroup" class="q-mr-sm" />
            <q-btn label="Annuler" color="grey" @click="showCreateGroupModal = false" flat />
          </q-card-section>
        </q-card>
      </q-dialog>
    </q-drawer>

    <q-page-container class="q-gutter-md">
      <router-view />
    </q-page-container>

    <q-footer class="bg-grey-8 text-white">
      <q-toolbar>
        <q-toolbar-title>
          © 2025 Mind vs Wild
        </q-toolbar-title>
      </q-toolbar>
    </q-footer>

  </q-layout>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useGroupStore } from '@/stores/group'

const authStore = useAuthStore()
const router = useRouter()
const groupStore = useGroupStore()

// Drawer state
const rightDrawerOpen = ref(false)
const groups = ref([])
const showCreateGroupModal = ref(false)
const newGroupName = ref('')
const newGroupDesc = ref('')

function toggleRightDrawer() {
  rightDrawerOpen.value = !rightDrawerOpen.value
}

// Restore user on mount
onMounted(async () => {
  await authStore.restoreUser()
  if (authStore.isLoggedIn) {
    await groupStore.fetchGroups()
    groups.value = groupStore.groups
  }
})

// Ajouter un watcher sur l'état de connexion
watch(() => authStore.isLoggedIn, async (newValue) => {
  if (newValue) {
    await groupStore.fetchGroups()
    groups.value = groupStore.groups
  } else {
    groups.value = []
  }
})

const isLoggedIn = computed(() => authStore.isLoggedIn)

function goToProfile() {
  rightDrawerOpen.value = false
  router.push('/profile')
}

function goToGroupDetail(id) {
  rightDrawerOpen.value = false
  router.push(`/groups/${id}`)
}

async function createGroup() {
  if (!newGroupName.value) {
    $q.notify({ type: 'warning', message: 'Veuillez saisir un nom pour le groupe.' })
    return
  }
  try {
    await groupStore.createGroup(newGroupName.value, newGroupDesc.value)
    groups.value = groupStore.groups
    newGroupName.value = ''
    newGroupDesc.value = ''
    showCreateGroupModal.value = false
    $q.notify({ type: 'positive', message: 'Groupe créé avec succès !' })
  } catch (err) {
    console.error('Erreur lors de la création du groupe :', err)
    $q.notify({
      type: 'negative',
      message: err?.response?.data?.detail || 'Impossible de créer le groupe.'
    })
  }
}
</script>


<style scoped>
.my-header {
  padding-top: 1rem;
  padding-left: 1.25rem;
  padding-right: 1.25rem;
}
</style>
