import { defineStore } from 'pinia'
import axios from 'axios'
import { useGroupStore } from './group'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
  }),
  getters: {
    isLoggedIn: (state) => !!state.token && !!state.user,
  },
  actions: {
    async login(username, password) {
      try {
        const response = await axios.post(`${import.meta.env.VITE_BACKEND_URL}/api/auth/login/`, {
          username,
          password,
        })

        if (response.status === 200) {
          this.token = response.data.token
          this.user = response.data.user
          localStorage.setItem('token', this.token)
          
          // load groups after login
          const groupStore = useGroupStore()
          await groupStore.fetchGroups()
          
          return true
        }
      } catch (err) {
        console.error('Erreur lors de la connexion:', err)
        return false
      }
    },

    async restoreUser() {
      const savedToken = localStorage.getItem('token')

      if (!savedToken) {
        this.user = null
        this.token = null
        return
      }

      try {
        const response = await axios.get(`${import.meta.env.VITE_BACKEND_URL}/api/auth/get_user/`, {
          headers: { Authorization: `Token ${savedToken}` },
        })

        if (response.status === 200) {
          this.token = savedToken
          this.user = response.data.user
        } else {
          this.logout()
        }
      } catch (err) {
        console.error('Erreur restoreUser:', err)
        this.logout()
      }
    },

    async logout() {
      try {
        if (this.token) {
          // Call logout API
          await axios.post(`${import.meta.env.VITE_BACKEND_URL}/api/auth/logout/`, {}, {
            headers: { Authorization: `Token ${this.token}` }
          });
        }
      } catch (err) {
        console.error('Erreur lors de la déconnexion:', err);
      } finally {
        // Clear the token and user data
        this.token = null;
        this.user = null;
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
    },
  },
})
