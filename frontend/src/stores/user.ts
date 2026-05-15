import { getGetUserProfileQueryKey } from '@/api/accounts/accounts'
import { useQueryClient } from '@tanstack/vue-query'
import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', () => {
  const queryClient = useQueryClient()

  function setTokens(data: { access: string; refresh: string; onboarding_required?: boolean }) {
    localStorage.setItem('access', data.access)
    localStorage.setItem('refresh', data.refresh)

    if (data.onboarding_required) {
      localStorage.setItem('needs_onboarding', '1')
    } else {
      localStorage.removeItem('needs_onboarding')
    }
  }

  function getTokens() {
    return {
      access: localStorage.getItem('access'),
      refresh: localStorage.getItem('refresh'),
      needsOnboarding: localStorage.getItem('needs_onboarding'),
    }
  }

  function removeTokens() {
    localStorage.removeItem('access')
    localStorage.removeItem('refresh')
    localStorage.removeItem('needs_onboarding')
  }

  function logout() {
    removeTokens()
    queryClient.resetQueries({ queryKey: getGetUserProfileQueryKey() })
  }

  return {
    getTokens,
    setTokens,
    removeTokens,
    logout,
  }
})
