export const homeRoutes = [
  {
    path: '/',
    component: () => import('./pages/HomePage.vue'),
    meta: { requiresAuth: true },
  },
]
