<template>
    <div v-if="user">
      <h1>Welcome, {{ user.username }}!</h1>
      <p>Email: {{ user.email }}</p>
      <button @click="updateUser">Update Profile</button>
      <button @click="deleteUser">Delete Account</button>
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
  
      const updateUser = () => {
        console.log('Update profile logic');
      };
  
      const deleteUser = async () => {
        try {
          await axios.delete('/api/user/', {
            headers: { Authorization: `Token ${token}` }
          });
          alert('Your account has been deleted');
        } catch (error) {
          console.error('Error deleting user:', error);
        }
      };
  
      onMounted(() => {
        getUserProfile();
      });
  
      return {
        user,
        updateUser,
        deleteUser
      };
    }
  });
  </script>
  
  <style scoped>
  </style>
  