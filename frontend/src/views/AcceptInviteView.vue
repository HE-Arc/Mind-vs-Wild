<template>
  <q-page class="q-pa-md">
    <div v-if="loading">
      <q-spinner size="lg" />
    </div>
    <div v-else>
      <h2>Acceptation de l'invitation</h2>
      <q-banner v-if="error" class="q-mt-md bg-negative text-white">
        {{ error }}
      </q-banner>
      <q-banner v-else-if="success" class="q-mt-md bg-positive text-white">
        Invitation acceptée avec succès ! Vous avez rejoint {{ joinedGroup?.name }}.
      </q-banner>
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGroupStore } from '@/stores/group'

const route = useRoute()
const router = useRouter()
const groupStore = useGroupStore()

const loading = ref(true)
const error = ref('')
const success = ref(false)
const joinedGroup = ref(null)

onMounted(async () => {
  const token = route.params.token
  if (!token) {
    error.value = "Token d'invitation manquant."
    loading.value = false
    return
  }

  try {
    const group = await groupStore.acceptInvite(token)
    joinedGroup.value = group
    success.value = true
  } catch (err) {
    console.error("Erreur acceptation invitation:", err)
    error.value = err?.response?.data?.detail || "Erreur lors de l'acceptation de l'invitation."
  } finally {
    loading.value = false
  }
})
</script>
