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
        <q-btn dense flat to="/groups" label="Groups" />
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
          <q-item class="text-black">
            <q-item-section avatar>
              <q-avatar>
                <img :src="authStore.user.profilePicture" alt="Profile Picture" />
              </q-avatar>
            </q-item-section>
            <q-item-section>
              <q-item-label>{{ authStore.user.username }}</q-item-label>
            </q-item-section>
          </q-item>
          <q-separator />
          <q-item clickable class="text-black">
            <q-item-section>Invitations</q-item-section>
          </q-item>
          <q-item clickable class="text-black">
            <q-item-section>Notifications</q-item-section>
          </q-item>
          <q-separator />
          <q-item clickable @click="goToProfile" class="text-black">
            <q-item-section>Profil</q-item-section>
          </q-item>
          <q-item clickable @click="logout" class="text-black">
            <q-item-section>Se déconnecter</q-item-section>
          </q-item>
        </template>
      </q-list>
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/useAuthStore'

const authStore = useAuthStore()
const router = useRouter()

// Drawer state
const rightDrawerOpen = ref(false)
function toggleRightDrawer() {
  rightDrawerOpen.value = !rightDrawerOpen.value
}

// Restore user on mount
onMounted(async () => {
  await authStore.restoreUser()
})

const isLoggedIn = computed(() => authStore.isLoggedIn)

function goToProfile() {
  rightDrawerOpen.value = false
  router.push('/profile')
}

function logout() {
  rightDrawerOpen.value = false
  authStore.logout()
}
</script>


<style scoped>
.my-header {
  padding-top: 1rem;
  padding-left: 1.25rem;
  padding-right: 1.25rem;
}
</style>
