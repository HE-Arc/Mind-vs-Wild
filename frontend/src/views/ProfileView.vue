<template>
  <q-page class="q-pa-md">
    <div class="row q-col-gutter-md full-width">
      <div class="col-12 col-md-4">
        <q-card class="column full-height">
          <q-card-section class="column items-center">
            <q-avatar size="140px" class="q-mb-md">
              <img :src="authStore.user?.avatar_url" :alt="authStore.user?.username" />
            </q-avatar>
            <q-input 
              rounded 
              standout 
              class="profile-input" 
              v-model="user.username" 
              bg-color="white" 
              color="black"
              input-style="color: black;" 
              label="Nom d'utilisateur" 
              maxlength="20"
              :rules="[
                v => v.length <= 20 || 'Le nom d\'utilisateur ne peut pas dépasser 20 caractères'
              ]"
            />
            <q-btn rounded class="profile-btn" label="Modifier le nom d'utilisateur" @click="update_user" />
          </q-card-section>
        </q-card>
      </div>

      <div class="col-12 col-md-4">
        <q-card class="column full-height">
          <q-card-section class="column items-center">
            <div class="text-h6 q-mb-xl">Mot de passe</div>
            <q-input 
              rounded 
              standout 
              class="profile-input" 
              v-model="password" 
              type="password" 
              label="Nouveau mot de passe"
              bg-color="white" 
              color="black" 
              input-style="color: black;" 
              :rules="[
                v => !v || v.length >= 8 || 'Le mot de passe doit contenir au moins 8 caractères',
                v => !v || v.length <= 68 || 'Le mot de passe ne peut pas dépasser 68 caractères'
              ]"
            />
            <q-input 
              rounded 
              standout 
              class="profile-input" 
              v-model="confirmPassword" 
              type="password"
              label="Confirmer le mot de passe" 
              bg-color="white" 
              color="black" 
              input-style="color: black;" 
              :rules="[
                v => v === password || 'Les mots de passe ne correspondent pas'
              ]"
            />
            <q-btn rounded class="profile-btn" label="Modifier le mot de passe" @click="update_user" />
            <span class="text-negative q-mt-sm" v-if="message">{{ message }}</span>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-12 col-md-4">
        <q-card class="column full-height ">
          <q-card-section class="column items-center">
            <div class="text-h6 q-mb-xl">Email</div>
            <q-input rounded standout class="profile-input" v-model="user.email" bg-color="white" color="black"
              input-style="color: black;" label="Adresse email" />
            <q-btn rounded class="profile-btn" label="Modifier l'adresse email" @click="update_user" />
          </q-card-section>
        </q-card>
      </div>

      <div class="col-12 q-mt-md flex justify-center q-gutter-md">
        <q-btn rounded class="delete-btn" label="Supprimer le compte" @click="delete_user" />
        <q-btn rounded class="profile-btn" label="Se déconnecter" @click="logout" />
      </div>
    </div>
  </q-page>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth';


export default defineComponent({
  name: 'UserProfile',
  setup() {
    const user = ref<any>({});
    const avatarLoaded = ref(false);
    const password = ref('');
    const confirmPassword = ref('');
    const token = localStorage.getItem('token');
    const message = ref('');
    const rightDrawerOpen = ref(false);
    const authStore = useAuthStore();
    const currentAvatarType = ref(1);

    const getUserProfile = async () => {
      try {
        const response = await axios.get(`${import.meta.env.VITE_BACKEND_URL}/api/auth/get_user/`, {
          headers: { Authorization: `Token ${token}` },
          withCredentials: true
        });
        user.value = response.data.user;
        authStore.user = response.data.user;
      } catch (error) {
        console.error('Error fetching user profile:', error);
      }
    };

    function logout() {
      rightDrawerOpen.value = false
      authStore.logout()
    }

    const delete_user = async () => {
      try {
        await axios.delete(`${import.meta.env.VITE_BACKEND_URL}/api/auth/delete_user/`, {
          headers: { Authorization: `Token ${token}` }
        });
        localStorage.removeItem('token');
        window.location.href = '/login';
      } catch (error) {
        console.error('Delete failed:', error);
      }
    };

    const update_user = async () => {
      if (password.value !== confirmPassword.value) {
        message.value = 'Les mots de passe ne correspondent pas.';
        return;
      }

      try {
        const dataToUpdate: any = {};
        if (user.value.username) dataToUpdate.username = user.value.username;
        if (user.value.email) dataToUpdate.email = user.value.email;
        if (password.value) dataToUpdate.password = password.value;

        const response = await axios.patch(`${import.meta.env.VITE_BACKEND_URL}/api/auth/update_user/`, dataToUpdate, {
          headers: { Authorization: `Token ${token}` }
        });

        message.value = 'Profil mis à jour avec succès!';
      } catch (error) {
        console.error('Update failed:', error);
        message.value = 'Erreur lors de la mise à jour du profil.';
      }
    };

    const avatarUrl = computed(() => {
      return authStore.user?.avatar_url;
    });

    onMounted(() => {
      if (authStore.user) {
        user.value = { ...authStore.user };
      }
      getUserProfile();
    });

    return {
      user,
      logout,
      password,
      confirmPassword,
      delete_user,
      update_user,
      message,
      authStore,
      currentAvatarType,
      avatarLoaded,
      avatarUrl,
    };
  }
});
</script>

<style scoped>

.profile-input {
  width: 100%;
  margin-bottom: 20px;
}

.profile-btn {
  min-width: 200px;
  background-color: #EE7154;
  color: white;
}

.delete-btn {
  background-color: #EE7154;
  color: white;
  min-width: 200px;
}

.message {
  color: red;
  margin-top: 10px;
}

.q-card {
  background: #2c2c38;
  padding: 20px;
}
</style>
