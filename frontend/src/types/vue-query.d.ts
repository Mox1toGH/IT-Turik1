import type { ErrorResponse } from '@/api/backendAPINinja.schemas'
import type { ErrorType } from '@/lib/apiClient'

declare module '@tanstack/vue-query' {
  interface Register {
    defaultError: ErrorType<ErrorResponse>
  }
}
