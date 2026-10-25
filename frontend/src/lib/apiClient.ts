import Axios, { AxiosError, type AxiosRequestConfig, isAxiosError } from 'axios'
import { useUserStore } from '@/stores/user'
import router from '@/router'

const API_BASE: string = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function containsFile(data: unknown): boolean {
  if (data instanceof File || data instanceof Blob) return true
  if (Array.isArray(data)) return data.some(containsFile)
  if (data && typeof data === 'object') {
    return Object.values(data).some(containsFile)
  }
  return false
}

function toFormData(data: Record<string, unknown>): FormData {
  const formData = new FormData()

  for (const [key, value] of Object.entries(data)) {
    if (value === undefined || value === null) continue

    if (Array.isArray(value)) {
      // repeat the key for each item so DRF's ListField(child=FileField()) parses correctly
      value.forEach((item) =>
        formData.append(key, item instanceof File || item instanceof Blob ? item : String(item)),
      )
      continue
    }

    formData.append(key, value instanceof File || value instanceof Blob ? value : String(value))
  }

  return formData
}

function toApiPath(url: string | undefined): string | undefined {
  if (!url?.startsWith('http://') && !url?.startsWith('https://')) return url

  const parsedUrl = new URL(url)
  return `${parsedUrl.pathname}${parsedUrl.search}`
}

export const AXIOS_INSTANCE = Axios.create({
  baseURL: API_BASE,
  withCredentials: true,

  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  },
})

let csrfToken: string | null = null
let csrfRequest: Promise<string> | null = null

const SAFE_METHODS = new Set(['get', 'head', 'options', 'trace'])

async function getCsrfToken(): Promise<string> {
  if (csrfToken) return csrfToken
  if (!csrfRequest) {
    csrfRequest = Axios.get<{ csrf_token: string }>(`${API_BASE}/api/accounts/csrf`, {
      withCredentials: true,
      headers: { Accept: 'application/json' },
    })
      .then(({ data }) => {
        csrfToken = data.csrf_token
        return csrfToken
      })
      .finally(() => {
        csrfRequest = null
      })
  }
  return csrfRequest
}

type RetryConfig = AxiosRequestConfig & { _authRetry?: boolean }

AXIOS_INSTANCE.interceptors.request.use(async (config) => {
  config.withCredentials = true
  if (!SAFE_METHODS.has((config.method ?? 'get').toLowerCase())) {
    config.headers['X-CSRFToken'] = await getCsrfToken()
  }
  return config
})

AXIOS_INSTANCE.interceptors.response.use(
  (res) => res,
  async (err) => {
    if (err.response?.status === 401) {
      const original = err.config as RetryConfig | undefined
      const requestPath = toApiPath(original?.url) ?? ''
      const isSessionEndpoint = /\/accounts\/(?:login|google-login|token\/refresh|csrf|logout)(?:\?|$)/.test(
        requestPath,
      )
      if (original && !original._authRetry && !isSessionEndpoint) {
        original._authRetry = true
        try {
          await AXIOS_INSTANCE.post('/api/accounts/token/refresh', {})
          return AXIOS_INSTANCE(original)
        } catch {
          const store = useUserStore()
          store.clearSession()
          if (router.currentRoute.value.meta.requiresAuth) router.push('/login')
        }
      } else if (!isSessionEndpoint) {
        const store = useUserStore()
        store.clearSession()
      }

      try {
        if (!isSessionEndpoint && router.currentRoute.value.meta.requiresAuth) {
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

export const customInstance = <T>(
  config: AxiosRequestConfig,
  options?: AxiosRequestConfig,
): Promise<T> => {
  const finalConfig = {
    ...config,
    ...options,
    url: toApiPath(options?.url ?? config.url),
  }

  if (finalConfig.data instanceof FormData || (finalConfig.data && containsFile(finalConfig.data))) {
    if (!(finalConfig.data instanceof FormData)) {
      finalConfig.data = toFormData(finalConfig.data as Record<string, unknown>)
    }

    finalConfig.headers = {
      ...finalConfig.headers,
      'Content-Type': 'multipart/form-data',
    }
  }

  return AXIOS_INSTANCE(finalConfig).then(({ data }) => data)
}

export type ErrorType<Error> = Error & { _axiosError: AxiosError }

export type BodyType<BodyData> = BodyData
