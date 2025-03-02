<template>
  <q-page class="q-pa-md">
    <h2>Mes Groupes</h2>
    <q-list bordered separator>
      <q-item v-for="group in groups" :key="group.id" clickable @click="goToGroupDetail(group.id)">
        <q-item-section>
          <div>{{ group.name }}</div>
          <div class="text-subtitle2 text-grey">Description : {{ group.description }}</div>
        </q-item-section>
      </q-item>
    </q-list>

    <q-input v-model="newGroupName" label="Nom du Groupe" outlined dense />
    <q-input v-model="newGroupDesc" label="Description" outlined dense />
    <q-btn label="Créer Groupe" color="primary" @click="createGroup" class="q-mt-md" />
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useGroupStore } from '@/stores/group'

const groupStore = useGroupStore()
const groups = ref([])
const newGroupName = ref('')
const newGroupDesc = ref('')
const router = useRouter()

onMounted(async () => {
  await groupStore.fetchGroups()
  groups.value = groupStore.groups
})

const createGroup = async () => {
  if (!newGroupName.value) return
  await groupStore.createGroup(newGroupName.value, newGroupDesc.value)
  newGroupName.value = ''
  newGroupDesc.value = ''
}

const goToGroupDetail = (groupId) => {
  router.push({ name: 'group-detail', params: { id: groupId } })
}
</script>
