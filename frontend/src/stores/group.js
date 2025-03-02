import { defineStore } from 'pinia'
import axios from 'axios'

export const useGroupStore = defineStore('group', {
  state: () => ({
    groups: [],
    currentGroup: null,
  }),
  actions: {
    async fetchGroups() {
      const token = localStorage.getItem('token')
      const response = await axios.get('http://127.0.0.1:8000/api/groups/', {
        headers: { Authorization: `Token ${token}` },
      })
      this.groups = response.data
    },
    async createGroup(name, description) {
      const token = localStorage.getItem('token')
      const response = await axios.post(
        'http://127.0.0.1:8000/api/groups/',
        { name, description },
        { headers: { Authorization: `Token ${token}` } },
      )
      this.groups.push(response.data)
      return response.data
    },

    async inviteUser(groupId, username) {
      const token = localStorage.getItem('token')
      const url = `http://127.0.0.1:8000/api/groups/${groupId}/invite/`
      // body data (passe username si on veut nominatif)
      const data = {}
      if (username) {
        data.username = username
      }
      const response = await axios.post(url, data, {
        headers: { Authorization: `Token ${token}` },
      })
      // La réponse contient { invite_token, invite_url, expires_at, ... }
      return response.data
    },

    async acceptInvite(inviteToken) {
      const token = localStorage.getItem('token')
      const url = `http://127.0.0.1:8000/api/groups/accept-invite/${inviteToken}/`
      const response = await axios.post(
        url,
        {},
        {
          headers: { Authorization: `Token ${token}` },
        },
      )
      // Le backend renvoie normalement le group (ou un message). Imaginons qu'il renvoie le group.
      const joinedGroup = response.data

      // Soit on push le group dans this.groups
      this.groups.push(joinedGroup)
      // Ou on refetch tout :
      // await this.fetchGroups()

      return joinedGroup
    },

    async leaveGroup(groupId) {
      const token = localStorage.getItem('token')
      const url = `http://127.0.0.1:8000/api/groups/${groupId}/leave/`
      const response = await axios.post(
        url,
        {},
        {
          headers: { Authorization: `Token ${token}` },
        },
      )
      return response.data
    },
  },
})
