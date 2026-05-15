export const adminRoutes = [
  {
    path: '/admin',
    component: () => import('./pages/AdminPage.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/admin/role-codes',
    component: () => import('./pages/RoleCodesPage.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/admin/certificates',
    component: () => import('./pages/AdminCertificatesPage.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
]
