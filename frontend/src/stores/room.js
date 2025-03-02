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
      const response = await axios.get('http://127.0.0.1:8000/api/rooms/', {
        headers: { Authorization: `Token ${token}` },
      })
      this.rooms = response.data
    },

    async fetchRoomDetails(code) {
      const token = localStorage.getItem('token')
      const response = await axios.get(`http://127.0.0.1:8000/api/rooms/${code}/`, {
        headers: { Authorization: `Token ${token}` },
      })
      this.currentRoom = response.data
      return this.currentRoom
    },
    
    async joinRoomByCode(code) {
      const token = localStorage.getItem('token')
      const response = await axios.post(
        `http://127.0.0.1:8000/api/rooms/join/${code}/`,
        {},
        {
          headers: { Authorization: `Token ${token}` },
        },
      )
      this.currentRoom = response.data
      return response.data
    },
  },
})
