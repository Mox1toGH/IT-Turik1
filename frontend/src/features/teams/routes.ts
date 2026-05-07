export const teamsRoutes = [
  {
    path: '/teams',
    component: () => import('./pages/TeamsListPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/teams/create',
    component: () => import('./pages/TeamCreatePage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/teams/:id/edit',
    component: () => import('./pages/TeamEditPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/teams/:id',
    component: () => import('./pages/TeamDetailPage.vue'),
    meta: { requiresAuth: true },
  },
]
