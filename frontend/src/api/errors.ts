import { isAxiosError } from 'axios'

export interface ApiError {
  message: string
  code?: string
  errors?: Record<string, string[]>
}

export function parseApiError(error: unknown): ApiError | null {
  if (!error) return null

  if (isAxiosError(error)) {
    const data = error.response?.data

    if (data && typeof data === 'object') {
      // 1. Direct message
      if ('message' in data && typeof data.message === 'string') {
        return {
          message: data.message,
          code: (data as any).code,
          errors: (data as any).errors,
        }
      }

      // 2. DRF validation error { field: ["error"] }
      if ('detail' in data && typeof data.detail === 'string') {
        return { message: data.detail }
      }
      
      // 3. Fallback for validation errors
      return {
        message: 'Validation error',
        errors: data as Record<string, string[]>,
      }
    }

    return { message: error.message || 'An unexpected error occurred' }
  }

  if (error instanceof Error) {
    return { message: error.message }
  }

  return { message: String(error) }
}
