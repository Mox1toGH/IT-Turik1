import { getTournament, getTournamentArchive } from '@/api/tournaments/tournaments'

const parsePositiveId = (rawId: unknown): number | null => {
  const value = Number(rawId)
  if (!Number.isInteger(value) || value <= 0) return null
  return value
}

const ensureTournamentExists = async (rawId: unknown) => {
  const id = parsePositiveId(rawId)
  if (!id) return { name: 'not-found' as const }

  try {
    await getTournament(id)
    return true
  } catch {
    return { name: 'not-found' as const }
  }
}

const ensureTournamentArchiveExists = async (rawId: unknown) => {
  const id = parsePositiveId(rawId)
  if (!id) return { name: 'not-found' as const }

  try {
    await getTournamentArchive(id)
    return true
  } catch {
    return { name: 'not-found' as const }
  }
}

export const tournamentsRoutes = [
  {
    path: '/tournaments/create',
    component: () => import('./pages/TournamentCreatePage.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/tournaments/:id/edit',
    component: () => import('./pages/TournamentEditPage.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    beforeEnter: (to) => ensureTournamentExists(to.params.id),
  },
  {
    path: '/tournaments',
    component: () => import('./pages/TournamentsListPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/tournaments/archive',
    component: () => import('./pages/TournamentArchivePage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/tournaments/archive/:id',
    component: () => import('./pages/TournamentArchiveDetailPage.vue'),
    meta: { requiresAuth: true },
    beforeEnter: (to) => ensureTournamentArchiveExists(to.params.id),
  },
  {
    path: '/tournaments/:id',
    component: () => import('./pages/TournamentPage.vue'),
    meta: { requiresAuth: true },
    beforeEnter: (to) => ensureTournamentExists(to.params.id),
  },
  {
    path: '/tournaments/:id/rounds/create',
    component: () => import('./pages/CreateRoundPage.vue'),
    meta: { requiresAuth: true },
    beforeEnter: (to) => ensureTournamentExists(to.params.id),
  },
]
