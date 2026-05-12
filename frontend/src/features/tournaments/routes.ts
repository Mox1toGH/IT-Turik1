export const tournamentsRoutes = [
  {
    path: '/tournaments/create',
    component: () => import('./pages/TournamentCreatePage.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/tournaments',
    component: () => import('./pages/TournamentsListPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/tournaments/:id',
    component: () => import('./pages/TournamentPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/tournaments/:id/rounds/create',
    component: () => import('./pages/CreateRoundPage.vue'),
    meta: { requiresAuth: true },
  },
]
