<template>
  <q-page class="profile-page">
    <q-card class="profile-card">
      <q-input rounded standout class="profile-input" v-model="user.username" bg-color="white" color="black"
        input-style="color: black;" />
      <q-btn rounded class="profile-btn" label="Modifier le nom d'utilisateur" @click="update_user" />

      <q-input rounded standout class="profile-input" v-model="user.email" bg-color="white" color="black"
        input-style="color: black;" />
      <q-btn rounded class="profile-btn" label="Modifier l'adresse email" @click="update_user" />

      <q-input rounded standout class="profile-input" v-model="password" type="password"
        label="Modifier le mot de passe" bg-color="white" color="black" input-style="color: black;" />
      <q-input rounded standout class="profile-input" v-model="confirmPassword" type="password"
        label="Confirmer le mot de passe" bg-color="white" color="black" input-style="color: black;" />
      <q-btn rounded class="profile-btn" label="Modifier le mot de passe" @click="update_user" />

      <q-btn rounded class="delete-btn" label="Supprimer le compte" @click="delete_user" />
      <q-btn rounded class="profile-btn" label="Se déconnecter" @click="logout" />
    </q-card>
  </q-page>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router'

export default defineComponent({
  name: 'UserProfile',
  setup() {
    const user = ref<any>({});
    const password = ref('');
    const confirmPassword = ref('');
    const token = localStorage.getItem('token');
    const message = ref('');
    const router = useRouter()

    const getUserProfile = async () => {
      try {
        const response = await axios.get(`${import.meta.env.VITE_BACKEND_URL}/api/auth/get/`, {
          headers: { Authorization: `Token ${token}` },
          withCredentials: true
        });
        user.value = response.data.user;
      } catch (error) {
        console.error('Error fetching user profile:', error);
      }
    };

    const logout = async () => {
      try {
        await axios.post(
          `${import.meta.env.VITE_BACKEND_URL}/api/auth/logout/`,
          {},
          { headers: { Authorization: `Token ${token}` } }
        );

        localStorage.removeItem('token');

        router.push('/login');
      } catch (error) {
        console.error('Logout failed:', error);
      }
    };

    const delete_user = async () => {
      try {
        await axios.delete(`${import.meta.env.VITE_BACKEND_URL}/api/auth/delete/`, {
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

        const response = await axios.patch(`${import.meta.env.VITE_BACKEND_URL}/api/auth/update/`, dataToUpdate, {
          headers: { Authorization: `Token ${token}` }
        });

        message.value = 'Profil mis à jour avec succès!';
      } catch (error) {
        console.error('Update failed:', error);
        message.value = 'Erreur lors de la mise à jour du profil.';
      }
    };

    onMounted(() => {
      getUserProfile();
    });

    return {
      user,
      logout,
      password,
      confirmPassword,
      delete_user,
      update_user,
      message
    };
  }
});
</script>

<style scoped>
.profile-page {
  min-height: calc(100vh - 60px);
  display: flex;
  justify-content: center;
  align-items: end;
}

.profile-card {
  min-height: 80vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  background: #2c2c38;
  padding: 20px;
  border-radius: 10px;
  margin: 10px;
  width: auto;
  flex-grow: 1;
  max-width: 350px;
  justify-content: space-between;
}

.profile-input {
  width: 100%;
  margin: 10px 0;
}

.profile-btn {
  width: 100%;
  margin-bottom: 10px;
  background-color: #EE7154;
  color: white;
}

.delete-btn {
  width: 100%;
  background-color: #EE7154;
  margin-bottom: 10px;
  color: white;
}

.message {
  color: red;
  margin-top: 10px;
}
</style>
