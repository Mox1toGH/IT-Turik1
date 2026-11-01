import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import NotFoundView from '@/features/not-found-page/NotFoundPage.vue'
import { authRoutes } from '@/features/auth/routes'
import { profileRoutes } from '@/features/profile/routes'
import { homeRoutes } from '@/features/home/routes'
import { adminRoutes } from '@/features/admin/routes'
import { teamsRoutes } from '@/features/teams/routes'
import { tournamentsRoutes } from '@/features/tournaments/routes'
import { newsRoutes } from '@/features/news/routes'
import { evaluationRoutes } from '@/features/evaluation/routes'
import { calendarRoutes } from '@/features/calendar/routes'
import { archiveRoutes } from '@/features/archive/routes'
import { getUserProfile } from '@/api/accounts/accounts'
import { hasAnyRole } from '@/shared/lib/permissions'
import type { UserRole } from '@/shared/types/user'

declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    requiresGuest?: boolean
    roles?: UserRole[]
    fullscreen?: boolean
  }
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    ...homeRoutes,
    ...authRoutes,
    ...profileRoutes,
    ...adminRoutes,
    ...teamsRoutes,
    ...tournamentsRoutes,
    ...newsRoutes,
    ...evaluationRoutes,
    ...calendarRoutes,
    ...archiveRoutes,
    { path: '/:pathMatch(.*)*', name: 'not-found', component: NotFoundView },
  ],
})

router.beforeEach(async (to) => {
  const store = useUserStore()
  let profile: Awaited<ReturnType<typeof getUserProfile>> | null = null

  // The session lives in HttpOnly cookies, so validate it once instead of
  // trying to inspect an access token in browser storage.
  if (!store.sessionChecked) {
    try {
      profile = await getUserProfile()
      store.setSession({ authenticated: true, onboarding_required: profile.needs_onboarding })
    } catch {
      store.clearSession()
    }
  }

  const isAuthenticated = store.isAuthenticated
  const needsOnboarding = store.needsOnboarding

  if (isAuthenticated && needsOnboarding && to.path !== '/complete-profile') {
    return '/complete-profile'
  }

  if (isAuthenticated && !needsOnboarding && to.path === '/complete-profile') {
    return '/'
  }

  if (to.meta.requiresAuth && !isAuthenticated) {
    return '/login'
  }

  if (
    to.meta.requiresGuest &&
    isAuthenticated &&
    !to.path.startsWith('/activate/') &&
    !to.path.startsWith('/reset-password/')
  ) {
    return '/'
  }

  if (to.meta.roles?.length) {
    try {
      profile ??= await getUserProfile()
      if (!isAuthenticated) return '/login'
      if (!hasAnyRole(profile, to.meta.roles)) {
        return '/'
      }
    } catch {
      store.clearSession()
      return '/'
    }
  }
})

export default router
