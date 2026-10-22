import type { ApiErrorResponse } from '@/shared/types/apiError'
import type { ErrorType } from '@/lib/apiClient'

declare module '@tanstack/vue-query' {
  interface Register {
    defaultError: ErrorType<ApiErrorResponse>
  }
}
