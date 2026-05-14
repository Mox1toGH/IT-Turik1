/**
 * Compatibility shim for api error parsing.
 * The apiClient interceptor transforms AxiosErrors into shaped objects
 * { code, message, details }. This helper extracts that shape.
 */

export interface ParsedApiError {
  code: string
  message: string
  details: Record<string, string[]> | null
}

export function parseApiError(error: unknown): ParsedApiError | null {
  if (!error || typeof error !== 'object') return null
  const e = error as Record<string, unknown>
  if (typeof e.code === 'string' || typeof e.message === 'string') {
    return {
      code: (e.code as string) ?? 'unknown_error',
      message: (e.message as string) ?? 'An error occurred.',
      details: (e.details as Record<string, string[]>) ?? null,
    }
  }
  return null
}
