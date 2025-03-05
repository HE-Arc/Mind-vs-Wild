<template>
  <q-page class="q-pa-md flex-center">
    <div class="text-center q-mb-md">
      <h2 class="text-white text-h5 q-ma-none">Mes Groupes</h2>
      <div class="text-subtitle2 text-grey-3">
        Liste des groupes auxquels je participe
      </div>
    </div>

    <q-card bordered class="q-pa-md q-mb-md card-width">
      <q-card-section>
        <div class="text-subtitle1 text-primary q-mb-md">
          Groupes Actuels
        </div>

        <q-list bordered>
          <q-item v-for="group in groups" :key="group.id" clickable @click="goToGroupDetail(group.id)">
            <q-item-section>
              <div class="text-body1">{{ group.name }}</div>
              <div class="text-caption text-grey-7">
                {{ group.description || 'Aucune description' }}
              </div>
            </q-item-section>

            <q-item-section side top>
              <q-icon name="chevron_right" />
            </q-item-section>
          </q-item>
        </q-list>
      </q-card-section>
    </q-card>

    <q-card bordered class="q-pa-md">
      <q-card-section>
        <div class="text-subtitle1 text-primary q-mb-md">
          Créer un Nouveau Groupe
        </div>

        <q-input v-model="newGroupName" label="Nom du groupe" outlined class="q-mb-md" />
        <q-input v-model="newGroupDesc" label="Description" type="textarea" outlined class="q-mb-md" />

        <q-btn label="Créer Groupe" color="primary" @click="createGroup" />
      </q-card-section>
    </q-card>

  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { useGroupStore } from '@/stores/group'

const router = useRouter()
const $q = useQuasar()
const groupStore = useGroupStore()

// Data local
const groups = ref([])
const newGroupName = ref('')
const newGroupDesc = ref('')

onMounted(async () => {
  await groupStore.fetchGroups()
  groups.value = groupStore.groups
})

function goToGroupDetail(id) {
  router.push(`/groups/${id}`)
}

async function createGroup() {
  if (!newGroupName.value) {
    $q.notify({ type: 'warning', message: 'Veuillez saisir un nom pour le groupe.' })
    return
  }
  // New group creation
  try {
    const newGroup = await groupStore.createGroup(newGroupName.value, newGroupDesc.value)
    groups.value.push(newGroup)
    newGroupName.value = ''
    newGroupDesc.value = ''
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

<style scoped></style>
