export interface ApiErrorResponse {
  message: string
  details?: Record<string, string> | null
}
