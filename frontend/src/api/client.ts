import { useUserStore } from '@/stores/user'
import axios from 'axios'

export const API_BASE: string = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    Accept: 'application/json',
  },
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type']
  } else {
    config.headers['Content-Type'] = 'application/json'
  }
  return config
})

apiClient.interceptors.response.use(
  (res) => res,
  async (err) => {
    if (err.response?.status === 401) {
      const store = useUserStore()
      if (store.getTokens().access) {
        store.removeTokens()
      }

      try {
        const { default: router } = await import('@/router')
        if (router.currentRoute.value.meta.requiresAuth) {
          router.push('/login')
        }
      } catch {
        // ignore
      }
    }

    return Promise.reject(err)
  },
)
