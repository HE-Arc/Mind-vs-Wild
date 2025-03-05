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
      const response = await axios.get(`${import.meta.env.VITE_BACKEND_URL}/api/groups/`, {
        headers: { Authorization: `Token ${token}` },
      })
      this.groups = response.data
    },
    async createGroup(name, description) {
      const token = localStorage.getItem('token')
      const response = await axios.post(
        `${import.meta.env.VITE_BACKEND_URL}/api/groups/`,
        { name, description },
        { headers: { Authorization: `Token ${token}` } },
      )
      this.groups.push(response.data)
      return response.data
    },

    async inviteUser(groupId, username) {
      const token = localStorage.getItem('token')
      const url = `${import.meta.env.VITE_BACKEND_URL}/api/groups/${groupId}/invite/`
      const data = {}
      if (username) {
        data.username = username
      }
      const response = await axios.post(url, data, {
        headers: { Authorization: `Token ${token}` },
      })
      return response.data
    },

    async acceptInvite(inviteToken) {
      const token = localStorage.getItem('token')
      const url = `${import.meta.env.VITE_BACKEND_URL}/api/groups/accept-invite/${inviteToken}/`
      const response = await axios.post(
        url,
        {},
        {
          headers: { Authorization: `Token ${token}` },
        },
      )

      // Add the joined group to the list of groups the user is in
      const joinedGroup = response.data
      this.groups.push(joinedGroup)

      return joinedGroup
    },

    async leaveGroup(groupId) {
      const token = localStorage.getItem('token')
      const url = `${import.meta.env.VITE_BACKEND_URL}/api/groups/${groupId}/leave/`
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
