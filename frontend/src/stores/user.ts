import { getGetUserProfileQueryKey } from '@/api/accounts/accounts'
import { useQueryClient } from '@tanstack/vue-query'
import { defineStore } from 'pinia'
import { connectNotificationSocket, setNotificationSocketAuthenticated } from '@/lib/notificationSocket'
import { setLeaderboardSocketAuthenticated } from '@/lib/leaderboardSocket'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const queryClient = useQueryClient()
  const isAuthenticated = ref(false)
  const needsOnboarding = ref(false)
  const sessionChecked = ref(false)

  function setSession(data: { authenticated?: boolean; onboarding_required?: boolean }) {
    isAuthenticated.value = data.authenticated ?? true
    needsOnboarding.value = Boolean(data.onboarding_required)
    sessionChecked.value = true
    setNotificationSocketAuthenticated(isAuthenticated.value)
    setLeaderboardSocketAuthenticated(isAuthenticated.value)
    if (isAuthenticated.value) connectNotificationSocket(queryClient)
  }

  function markSessionChecked() {
    sessionChecked.value = true
  }

  function clearSession() {
    isAuthenticated.value = false
    needsOnboarding.value = false
    sessionChecked.value = true
    setNotificationSocketAuthenticated(false)
    setLeaderboardSocketAuthenticated(false)
  }

  async function logout() {
    try {
      const { AXIOS_INSTANCE } = await import('@/lib/apiClient')
      await AXIOS_INSTANCE.post('/api/accounts/logout')
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
    setSession,
    markSessionChecked,
    clearSession,
    logout,
  }
})
