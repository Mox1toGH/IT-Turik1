import { getGetUserProfileQueryKey, getGetUserProfileQueryOptions } from '@/api/accounts/accounts'
import type { GetUserProfileResponse } from '@/api/backendAPINinja.schemas'
import { useQueryClient } from '@tanstack/vue-query'
import { defineStore } from 'pinia'
import {
  connectNotificationSocket,
  setNotificationSocketAuthenticated,
} from '@/lib/notificationSocket'
import { getGetUnreadNotificationCountQueryKey } from '@/api/notifications/notifications'
import { setLeaderboardSocketAuthenticated } from '@/lib/leaderboardSocket'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const queryClient = useQueryClient()
  const isAuthenticated = ref(false)
  const needsOnboarding = ref(false)
  const sessionChecked = ref(false)
  const profile = ref<GetUserProfileResponse | null>(null)
  let sessionCheck: Promise<GetUserProfileResponse | null> | null = null

  function setSession(
    data: { authenticated?: boolean; onboarding_required?: boolean },
    userProfile?: GetUserProfileResponse,
  ) {
    isAuthenticated.value = data.authenticated ?? true
    needsOnboarding.value = Boolean(data.onboarding_required)
    sessionChecked.value = true
    profile.value = userProfile ?? null
    setNotificationSocketAuthenticated(isAuthenticated.value)
    setLeaderboardSocketAuthenticated(isAuthenticated.value)
    if (isAuthenticated.value) {
      if (userProfile) {
        queryClient.setQueryData(getGetUserProfileQueryKey(), userProfile)
      } else {
        queryClient.invalidateQueries({ queryKey: getGetUserProfileQueryKey() })
      }
      queryClient.invalidateQueries({ queryKey: getGetUnreadNotificationCountQueryKey() })
      connectNotificationSocket(queryClient)
    }
  }

  async function checkSession() {
    if (sessionChecked.value) return profile.value
    if (sessionCheck) return sessionCheck

    sessionCheck = queryClient
      .fetchQuery(getGetUserProfileQueryOptions())
      .then((userProfile) => {
        setSession(
          { authenticated: true, onboarding_required: userProfile.needs_onboarding },
          userProfile,
        )
        return userProfile
      })
      .catch(() => {
        clearSession()
        return null
      })
      .finally(() => {
        sessionCheck = null
      })

    return sessionCheck
  }

  async function ensureProfile() {
    if (!isAuthenticated.value) return null
    if (profile.value) return profile.value

    try {
      profile.value = await queryClient.fetchQuery(getGetUserProfileQueryOptions())
      return profile.value
    } catch {
      clearSession()
      return null
    }
  }

  function clearSession() {
    isAuthenticated.value = false
    needsOnboarding.value = false
    sessionChecked.value = true
    profile.value = null
    setNotificationSocketAuthenticated(false)
    setLeaderboardSocketAuthenticated(false)
  }

  async function logout() {
    try {
      const { AXIOS_INSTANCE, resetCsrfToken } = await import('@/lib/apiClient')
      try {
        await AXIOS_INSTANCE.post('/api/accounts/logout', {}, { skipAuthRefresh: true })
      } finally {
        resetCsrfToken()
      }
    } catch {
      // Local logout still clears the UI session when the server is unavailable.
    }
    clearSession()
    queryClient.resetQueries({ queryKey: getGetUserProfileQueryKey() })
  }

  return {
    isAuthenticated,
    needsOnboarding,
    sessionChecked,
    profile,
    setSession,
    checkSession,
    ensureProfile,
    clearSession,
    logout,
  }
})
