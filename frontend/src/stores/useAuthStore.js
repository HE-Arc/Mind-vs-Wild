import { defineStore } from 'pinia'
import axios from 'axios'

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
        const response = await axios.get(`${import.meta.env.VITE_BACKEND_URL}/api/auth/get/`, {
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

    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
      window.location.href = '/login'
    },
  },
})
