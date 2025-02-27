<template>
  <q-layout>
    <q-page-container>
      <q-page class="profile-page">
        <q-card class="profile-card">
          <q-input rounded standout class="profile-input" v-model="user.username" bg-color="white" color="black"
            input-style="color: black;" />
          <q-btn rounded class="profile-btn" label="Change Username" @click="update_user" />

          <q-input rounded standout class="profile-input" v-model="user.email" bg-color="white" color="black"
            input-style="color: black;" />
          <q-btn rounded class="profile-btn" label="Change Email" @click="update_user" />

          <q-input rounded standout class="profile-input" v-model="password" type="password" label="Password"
            bg-color="white" color="black" input-style="color: black;" />
          <q-input rounded standout class="profile-input" v-model="confirmPassword" type="password"
            label="Confirm Password" bg-color="white" color="black" input-style="color: black;" />
          <q-btn rounded class="profile-btn" label="Change Password" @click="update_user" />

          <q-btn rounded class="delete-btn" label="Delete Account" @click="delete_user" />
          <q-btn rounded class="profile-btn" label="logout" @click="logout" />
        </q-card>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import axios from 'axios';

export default defineComponent({
  name: 'UserProfile',
  setup() {
    const user = ref<any>({});
    const password = ref('');
    const confirmPassword = ref('');
    const token = localStorage.getItem('token');
    const message = ref('');

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

        window.location.href = '/';
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
  max-width: 250px;
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
