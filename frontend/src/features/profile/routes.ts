export const profileRoutes = [
  {
    path: '/profile',
    component: () => import('./pages/ProfilePage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/users/:id',
    component: () => import('@/features/profile/pages/UserProfilePage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/profile/edit',
    component: () => import('./pages/EditProfilePage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/complete-profile',
    component: () => import('./pages/CompleteProfilePage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/activate/:uid/:token',
    component: () => import('./pages/ActivateProfilePage.vue'),
    meta: { requiresGuest: true },
  },
  {
    path: '/profile/notifications',
    component: () => import('./pages/NotificationsPage.vue'),
    meta: { requiresAuth: true },
  },
]
