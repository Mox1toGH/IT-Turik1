export const profileRoutes = [
  {
    path: '/profile',
    component: () => import('./pages/ProfilePage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/users/:id',
    component: () => import('./components/profile/sections/UserProfileSection.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/users/:id/points',
    component: () => import('./components/profile/sections/TransactionHistorySection.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/users/:id/tournaments-history',
    component: () => import('./components/profile/sections/UserTournamentHistorySection.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/profile/certificates',
    component: () => import('./components/profile/sections/CertificatesSection.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/complete-profile',
    component: () => import('./components/profile/sections/CompleteProfileSection.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/activate/:uid/:token',
    component: () => import('./components/profile/sections/ActivateProfileSection.vue'),
    meta: { requiresGuest: true },
  },
  {
    path: '/profile/notifications',
    component: () => import('./pages/NotificationsPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/profile/points',
    component: () => import('./components/profile/sections/TransactionHistorySection.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/profile/tournaments-history',
    component: () => import('./components/profile/sections/UserTournamentHistorySection.vue'),
    meta: { requiresAuth: true },
  },
]
