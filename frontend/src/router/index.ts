import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { accountsService } from '@/api/services/accounts'
import NotFoundView from '@/features/not-found-page/NotFoundPage.vue'
import { authRoutes } from '@/features/auth/routes'
import { profileRoutes } from '@/features/profile/routes'
import { homeRoutes } from '@/features/home/routes'
import { adminRoutes } from '@/features/admin/routes'
import { teamsRoutes } from '@/features/teams/routes'
import { tournamentsRoutes } from '@/features/tournaments/routes'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    ...homeRoutes,
    ...authRoutes,
    ...profileRoutes,
    ...adminRoutes,
    ...teamsRoutes,
    ...tournamentsRoutes,
    { path: '/:pathMatch(.*)*', name: 'not-found', component: NotFoundView },
  ],
})

router.beforeEach(async (to, _from, next) => {
  const store = useUserStore()
  const tokens = store.getTokens()

  const isAuthenticated = !!tokens.access
  const needsOnboarding = !!tokens.needsOnboarding

  if (isAuthenticated && needsOnboarding && to.path !== '/complete-profile') {
    next('/complete-profile')
    return
  }

  if (isAuthenticated && !needsOnboarding && to.path === '/complete-profile') {
    next('/')
    return
  }

  if (to.meta.requiresAuth && !isAuthenticated) {
    store.logout()
    next('/login')
    return
  }

  if (
    to.meta.requiresGuest &&
    isAuthenticated &&
    !to.path.startsWith('/activate/') &&
    !to.path.startsWith('/reset-password/')
  ) {
    next('/')
    return
  }

  if (to.meta.requiresAdmin) {
    try {
      const profile = await accountsService.getProfile()
      if (profile.role !== 'admin') {
        next('/')
        return
      }
    } catch {
      next('/')
      return
    }
  }

  next()
})

export default router
