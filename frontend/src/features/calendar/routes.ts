export const calendarRoutes = [
  {
    path: '/calendar',
    component: () => import('./pages/CalendarPage.vue'),
    meta: { requiresAuth: true },
  },
]
