export const evaluationRoutes = [
  {
    path: '/evaluation',
    component: () => import('./pages/JuryEvaluationPage.vue'),
    meta: { requiresAuth: true },
  },
]
