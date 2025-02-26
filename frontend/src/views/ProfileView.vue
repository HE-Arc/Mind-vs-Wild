<template>
  <div v-if="user">
    <h1>Welcome, {{ user.username }}!</h1>
    <p>Email: {{ user.email }}</p>
    <q-btn label="logout" @click="logout" />
  </div>
  <div v-else>
    <p>Loading...</p>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import axios from 'axios';

export default defineComponent({
  name: 'UserProfile',
  setup() {
    const user = ref<any>(null);
    const token = localStorage.getItem('token');

    const getUserProfile = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/auth/get/', {
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
      'http://127.0.0.1:8000/api/auth/logout/',
      {}, 
      { headers: { Authorization: `Token ${token}` } } 
    );

    localStorage.removeItem('token');

    window.location.href = '/';
  } catch (error) {
    console.error('Logout failed:', error);
  }
};

    onMounted(() => {
      getUserProfile();
    });

    return {
      user,
      logout
    };
  }
});
</script>

<style scoped></style>