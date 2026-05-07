export const authRoutes = [
  {
    path: '/login',
    component: () => import('./pages/LoginPage.vue'),
    meta: { requiresGuest: true },
  },
  {
    path: '/register',
    component: () => import('./pages/RegisterPage.vue'),
    meta: { requiresGuest: true },
  },
  { path: '/forgot-password', component: () => import('./pages/ForgotPasswordPage.vue') },
  {
    path: '/reset-password/:uid/:token',
    component: () => import('./pages/ResetPasswordPage.vue'),
    meta: { requiresGuest: true },
  },
]
