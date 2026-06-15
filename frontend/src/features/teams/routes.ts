import { getTeam } from '@/api/teams/teams'

const parsePositiveId = (rawId: unknown): number | null => {
  const value = Number(rawId)
  if (!Number.isInteger(value) || value <= 0) return null
  return value
}

const ensureTeamExists = async (rawId: unknown) => {
  const id = parsePositiveId(rawId)
  if (!id) return { name: 'not-found' as const }

  try {
    await getTeam(id)
    return true
  } catch {
    return { name: 'not-found' as const }
  }
}

export const teamsRoutes = [
  {
    path: '/teams',
    component: () => import('./pages/TeamsListPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/teams/create',
    component: () => import('./pages/TeamCreatePage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/teams/:id/edit',
    component: () => import('./pages/TeamEditPage.vue'),
    meta: { requiresAuth: true },
    beforeEnter: (to) => ensureTeamExists(to.params.id),
  },
  {
    path: '/teams/:id',
    component: () => import('./pages/TeamDetailPage.vue'),
    meta: { requiresAuth: true },
    beforeEnter: (to) => ensureTeamExists(to.params.id),
  },
]
