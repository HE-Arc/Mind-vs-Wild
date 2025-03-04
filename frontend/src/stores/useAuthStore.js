// useAuthStore.js
import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: null,
  }),
  actions: {
    async login(username, password) {
      try {
        const response = await axios.post('http://127.0.0.1:8000/api/auth/login/', {
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
        console.error('Login error:', err)
        return false
      }
    },
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
    },

    async restoreUser() {
      const savedToken = localStorage.getItem('token')
      if (!savedToken) {
        return
      }
      try {
        // On vérifie la validité du token via /api/auth/get/ (ou un endpoint équivalent)
        const response = await axios.get('http://127.0.0.1:8000/api/auth/get/', {
          headers: { Authorization: `Token ${savedToken}` },
        })
        if (response.status === 200) {
          this.token = savedToken
          this.user = response.data.user
        }
      } catch (err) {
        console.error('Erreur restoreUser:', err)
        // Si token invalide, on le retire
        localStorage.removeItem('token')
      }
    },
  },
})
