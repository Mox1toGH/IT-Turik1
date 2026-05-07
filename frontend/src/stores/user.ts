import type { LoginResponse } from '@/api/services/accounts/types'
import { accountKeys } from '@/api/queries/keys'
import { useQueryClient } from '@tanstack/vue-query'
import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', () => {
  const queryClient = useQueryClient()

  function setTokens(data: LoginResponse) {
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
    queryClient.resetQueries({ queryKey: accountKeys.profile() })
  }

  return {
    getTokens,
    setTokens,
    removeTokens,
    logout,
  }
})
