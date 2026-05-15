export const shopRoutes = [
  {
    path: '/shop',
    component: () => import('./pages/ShopPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/profile/orders',
    component: () => import('./pages/ShopOrderHistoryPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/profile/inventory',
    component: () => import('./pages/ShopInventoryPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/admin/shop-orders',
    component: () => import('./pages/ShopAdminOrdersPage.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
]
