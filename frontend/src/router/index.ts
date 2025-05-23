import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import ProfileView from '@/views/ProfileView.vue'
import RoomListView from '@/views/RoomListView.vue'
import RoomDetailView from '@/views/RoomDetailView.vue'
import GroupListView from '@/views/GroupListView.vue'
import GroupDetailView from '@/views/GroupDetailView.vue'
import AcceptInviteView from '@/views/AcceptInviteView.vue'
import { isAuthenticated } from '@/utils/auth.ts'

import type { NavigationGuardNext, RouteLocationNormalized } from 'vue-router';
import AboutView from '@/views/AboutView.vue'

const requireAuth = async (to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
  const isAuth = await isAuthenticated();
  if (isAuth) {
    next();
  } else {
    next('/login');
  }
};

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
      component: AboutView,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      beforeEnter: async (to, from, next) => {
        const isAuth = await isAuthenticated();
        if (isAuth) {
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
      beforeEnter: async (to, from, next) => {
        const isAuth = await isAuthenticated();
        if (isAuth) {
          next('/profile');
        } else {
          next();
        }
      }
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
      beforeEnter: requireAuth
    },
    {
      path: '/rooms',
      name: 'rooms',
      component: RoomListView,
      beforeEnter: requireAuth
    },
    {
      path: '/rooms/:id/join',
      name: 'join-room',
      component: RoomDetailView,
      beforeEnter: requireAuth
    },
    {
      path: '/rooms/:id',
      name: 'room-detail',
      component: RoomDetailView,
      beforeEnter: requireAuth
    },
    {
      path: '/rooms/:id/leave',
      name: 'leave-room',
      component: RoomListView,
      beforeEnter: requireAuth
    },
    {
      path: '/groups',
      name: 'groups',
      component: GroupListView,
      beforeEnter: requireAuth
    },
    {
      path: '/groups/:id',
      name: 'group-detail',
      component: GroupDetailView,
      beforeEnter: requireAuth
    },
    {
      path: '/groups/:id/leave',
      name: 'leave-group',
      component: GroupDetailView,
      beforeEnter: requireAuth
    },
    {
      path: '/groups/accept-invite/:token',
      name: 'accept-invite',
      component: AcceptInviteView,
    },
  ],
})

export default router;
