import { isAxiosError, type AxiosError } from 'axios'

export interface ApiError<DetailsFields extends string = string> {
  code: string
  message: string
  details: Partial<Record<DetailsFields, string[]>>
}

export function parseApiError<DetailsFields extends string = string>(
  error?: AxiosError<ApiError<DetailsFields>> | null,
): ApiError<DetailsFields> | undefined {
  if (isAxiosError<ApiError<DetailsFields>>(error)) {
    if (error.response?.data) {
      const data = error.response.data

      return data
    }

    if (error.request) {
      return {
        message: 'Network error. Try again',
        code: 'unexpected_error',
        details: {},
      }
    }
  }

  if (error instanceof Error) {
    return {
      message: error.message || 'Unexpected error. Try again',
      code: 'unexpected_error',
      details: {},
    }
  }
}
