export const calendarRoutes = [
  {
    path: '/calendar',
    component: () => import('./pages/CalendarPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/calendar/google-callback',
    component: () => import('./pages/GoogleCalendarCallbackPage.vue'),
    meta: { requiresAuth: true },
  },
]
