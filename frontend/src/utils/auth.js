// src/utils/auth.js
import axios from 'axios'

export const login = async (username, password) => {
  try {
    const response = await axios.post(
      `${import.meta.env.VITE_BACKEND_URL}/api/auth/login/`,
      {
        username,
        password,
      },
      {
        withCredentials: true,
      },
    )

    if (response.status === 200) {
      localStorage.setItem('token', response.data.token)
      return true
    } else {
      console.error('Login failed:', response.status, response.data)
      return false
    }
  } catch (error) {
    console.error('Error during login:', error)
    return false
  }
}

export const isAuthenticated = async () => {
  const token = localStorage.getItem('token')

  if (!token) {
    return false
  }

  try {
    const response = await axios.get(`${import.meta.env.VITE_BACKEND_URL}/api/auth/get/`, {
      headers: { Authorization: `Token ${token}` },
      withCredentials: true,
    })

    return response.status === 200
  } catch (error) {
    console.error('Erreur lors de la vérification du token:', error)
    localStorage.removeItem('token') // Supprime le token s'il est invalide
    return false
  }
}
