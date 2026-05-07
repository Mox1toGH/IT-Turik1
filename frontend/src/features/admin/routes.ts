export const adminRoutes = [
  {
    path: '/admin/role-codes',
    component: () => import('./pages/RoleCodesPage.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
]
