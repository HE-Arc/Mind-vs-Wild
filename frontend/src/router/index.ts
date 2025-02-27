import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import ProfileView from '@/views/ProfileView.vue'
import axios from 'axios'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      beforeEnter: (to, from, next) => {
        const token = localStorage.getItem('token');
        if (token) {
          next('/profile');
        } else {
          next(); 
        }
      }
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
      beforeEnter: async (to, from, next) => {
        const token = localStorage.getItem('token');

        if (token) {
          try {
            const response = await axios.get(`${import.meta.env.VITE_BACKEND_URL}/api/auth/get/`, {
              headers: { Authorization: `Token ${token}` },
              withCredentials: true
            });

            if (response.status === 200) {
              next(); 
            } else {
              next('/login'); 
            }
          } catch (error) {
            next('/login'); 
          }
        } else {
          next('/login');
        }
      }
    },
  ],
})

export default router
