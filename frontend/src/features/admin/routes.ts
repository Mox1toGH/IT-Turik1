export const adminRoutes = [
  {
    path: '/admin',
    component: () => import('./pages/AdminPage.vue'),
    meta: { requiresAuth: true, roles: ['admin'] },
  },
  {
    path: '/admin/role-codes',
    component: () => import('./pages/RoleCodesPage.vue'),
    meta: { requiresAuth: true, roles: ['admin'] },
  },
]
