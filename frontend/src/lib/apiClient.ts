import Axios, { AxiosError, type AxiosRequestConfig, isAxiosError } from 'axios'
import { useUserStore } from '@/stores/user'
import router from '@/router'

const API_BASE: string = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const AXIOS_INSTANCE = Axios.create({
  baseURL: API_BASE,
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  },
})

AXIOS_INSTANCE.interceptors.request.use((config) => {
  const token = localStorage.getItem('access')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

AXIOS_INSTANCE.interceptors.response.use(
  (res) => res,
  async (err) => {
    if (err.response?.status === 401) {
      const store = useUserStore()
      if (store.getTokens().access) {
        store.removeTokens()
      }

      try {
        if (router.currentRoute.value.meta.requiresAuth) {
          router.push('/login')
        }
      } catch {
        // ignore
      }
    }

    if (isAxiosError(err)) {
      if (err.response?.data) {
        return Promise.reject({
          ...err.response.data,
          _axiosError: err,
        })
      }
      if (err.request) {
        return Promise.reject({
          code: 'network_error',
          message: 'Network error. Try again',
          details: null,
          _axiosError: err,
        })
      }
    }

    return Promise.reject(err)
  },
)

// Add a second `options` argument to pass extra options to each query
export const customInstance = <T>(
  config: AxiosRequestConfig,
  options?: AxiosRequestConfig,
): Promise<T> => {
  const promise = AXIOS_INSTANCE({
    ...config,
    ...options,
  }).then(({ data }) => data)

  return promise
}

// Override the return error type for react-query and swr
export type ErrorType<Error> = Error & { _axiosError: AxiosError }

// Standard body type
export type BodyType<BodyData> = BodyData

// Or wrap the body type if processing data before sending
// export type BodyType<BodyData> = CamelCase<BodyData>;
