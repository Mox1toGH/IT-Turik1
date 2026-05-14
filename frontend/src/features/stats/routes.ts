export const statsRoutes = [
  {
    path: '/stats',
    component: () => import('./pages/StatsPage.vue'),
    meta: { requiresAuth: true },
  },
]
