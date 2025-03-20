import { defineStore } from 'pinia'
import axios from 'axios'

export const useRoomStore = defineStore('room', {
  state: () => ({
    rooms: [],
    currentRoom: null,
  }),
  actions: {
    async fetchRooms() {
      const token = localStorage.getItem('token')
      const response = await axios.get(`${import.meta.env.VITE_BACKEND_URL}/api/rooms/`, {
        headers: { Authorization: `Token ${token}` },
      })
      this.rooms = response.data
    },

    async fetchRoomDetails(id) {
      const token = localStorage.getItem('token')
      const response = await axios.get(`${import.meta.env.VITE_BACKEND_URL}/api/rooms/${id}/`, {
        headers: { Authorization: `Token ${token}` },
      })
      this.currentRoom = response.data
      return this.currentRoom
    },

    async joinRoom(id) {
      const token = localStorage.getItem('token')
      const response = await axios.post(
        `${import.meta.env.VITE_BACKEND_URL}/api/rooms/${id}/join/`,
        {},
        {
          headers: { Authorization: `Token ${token}` },
        },
      )
      this.currentRoom = response.data.room
      return response.data
    },

    async createRoom(name, groupId = null) {
      const token = localStorage.getItem('token')
      const response = await axios.post(
        `${import.meta.env.VITE_BACKEND_URL}/api/rooms/`,
        { name, group: groupId },
        {
          headers: { Authorization: `Token ${token}` },
        },
      )
      this.rooms.push(response.data)
      return response.data
    },

    async leaveRoom() {
      const token = localStorage.getItem('token')
      await axios.post(
        `${import.meta.env.VITE_BACKEND_URL}/api/rooms/${this.currentRoom.id}/leave/`,
        {},
        {
          headers: { Authorization: `Token ${token}` },
        },
      )
      this.currentRoom = null
    },
  },
})
