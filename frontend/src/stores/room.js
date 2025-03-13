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

    async fetchRoomDetails(code) {
      const token = localStorage.getItem('token')
      const response = await axios.get(`${import.meta.env.VITE_BACKEND_URL}/api/rooms/${code}/`, {
        headers: { Authorization: `Token ${token}` },
      })
      this.currentRoom = response.data
      return this.currentRoom
    },

    async joinRoomByCode(code) {
      const token = localStorage.getItem('token')
      const response = await axios.post(
        `${import.meta.env.VITE_BACKEND_URL}/api/rooms/join/${code}/`,
        {},
        {
          headers: { Authorization: `Token ${token}` },
        },
      )
      this.currentRoom = response.data
      return response.data
    },

    async createRoom(name, groupId) {
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
        `${import.meta.env.VITE_BACKEND_URL}/api/rooms/${this.currentRoom.code}/leave/`,
        {},
        {
          headers: { Authorization: `Token ${token}` },
        },
      )
      this.currentRoom = null
    },
  },
})
