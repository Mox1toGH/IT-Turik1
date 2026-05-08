import { apiClient } from '@/api/client'
import { isAxiosError } from 'axios'
import type { GetCertificatesResponse, GetCertificateTemplatesResponse, VerifyCertificateResponse } from './types'

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

  async getCertificates() {
    const { data } = await apiClient.get<GetCertificatesResponse>(`${prefix}/`)
    return Array.isArray(data) ? data : []
  },

  async createCertificate(body: {
    user: number
    tournament: number
    team?: number | null
    placement: string
    certificate_number?: string
    template?: number | null
  }) {
    const { data } = await apiClient.post(`${prefix}/`, body)
    return data
  },

  async getTemplates() {
    const { data } = await apiClient.get<GetCertificateTemplatesResponse>(`${prefix}/templates/`)
    return Array.isArray(data) ? data : []
  },

  async uploadTemplate(args: { name: string; image: File; is_default?: boolean }) {
    const formData = new FormData()
    formData.append('name', args.name)
    formData.append('image', args.image)
    formData.append('is_default', String(Boolean(args.is_default)))

    const { data } = await apiClient.post(`${prefix}/templates/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  },

  async verifyByCode(code: string) {
    const { data } = await apiClient.get<VerifyCertificateResponse>(`${prefix}/verify/${encodeURIComponent(code)}/`)
    return data
  },
}
