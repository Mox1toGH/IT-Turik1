export const newsRoutes = [
  {
    path: '/news',
    component: () => import('./pages/NewsPage.vue'),
    meta: { requiresAuth: true },
  },
]

