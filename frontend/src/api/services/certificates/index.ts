import { apiClient } from '@/api/client'
import { isAxiosError } from 'axios'
import type { GetCertificatesResponse } from './types'

const prefix = '/api/certificates'

export const certificatesService = {
  async getMyCertificates() {
    try {
      const { data } = await apiClient.get<GetCertificatesResponse>(`${prefix}/`)
      return Array.isArray(data) ? data : []
    } catch (error) {
      if (isAxiosError(error) && error.response?.status === 404) {
        return []
      }
      throw error
    }
  },
}
