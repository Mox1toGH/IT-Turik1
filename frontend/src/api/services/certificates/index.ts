import { apiClient } from '@/api/client'
import { isAxiosError } from 'axios'
import type {
  CertificateItem,
  CertificateTemplateItem,
  PaginatedResponse,
  VerifyCertificateResponse,
} from './types'

const prefix = '/api/certificates'

export const certificatesService = {
  async getMyCertificates(args?: { page?: number; pageSize?: number }) {
    const page = args?.page ?? 1
    const pageSize = args?.pageSize ?? 6

    try {
      const { data } = await apiClient.get<PaginatedResponse<CertificateItem> | CertificateItem[]>(
        `${prefix}/`,
        { params: { page, page_size: pageSize } },
      )
      if (Array.isArray(data)) {
        return {
          count: data.length,
          next: null,
          previous: null,
          results: data,
        }
      }
      return data
    } catch (error) {
      if (isAxiosError(error) && error.response?.status === 404) {
        return {
          count: 0,
          next: null,
          previous: null,
          results: [],
        }
      }
      throw error
    }
  },

  async getCertificates(args?: { page?: number; pageSize?: number; search?: string }) {
    const page = args?.page ?? 1
    const pageSize = args?.pageSize ?? 20
    const search = args?.search ?? ''

    const { data } = await apiClient.get<PaginatedResponse<CertificateItem> | CertificateItem[]>(
      `${prefix}/`,
      { params: { page, page_size: pageSize, search } },
    )
    if (Array.isArray(data)) {
      return {
        count: data.length,
        next: null,
        previous: null,
        results: data,
      }
    }
    return data
  },

  async updateCertificate(uniqueCode: string, body: Partial<{
    user: number
    tournament: number
    team?: number | null
    placement: string
    certificate_number?: string
    template?: number | null
  }>) {
    const { data } = await apiClient.patch(`${prefix}/${uniqueCode}/`, body)
    return data
  },

  async deleteCertificate(uniqueCode: string) {
    const { data } = await apiClient.delete(`${prefix}/${uniqueCode}/`)
    return data
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

  async getTemplates(args?: { page?: number; pageSize?: number; nopage?: boolean }) {
    const params: Record<string, any> = {}
    if (args?.page) params.page = args.page
    if (args?.pageSize) params.page_size = args.pageSize
    if (args?.nopage) params.nopage = 'true'

    const { data } = await apiClient.get<PaginatedResponse<CertificateTemplateItem> | CertificateTemplateItem[]>(
      `${prefix}/templates/`,
      { params }
    )
    if (Array.isArray(data)) {
      return {
        count: data.length,
        next: null,
        previous: null,
        results: data,
      }
    }
    return data
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

  async updateTemplate(id: number, args: { name?: string; image?: File; is_default?: boolean }) {
    const formData = new FormData()
    if (args.name) formData.append('name', args.name)
    if (args.image) formData.append('image', args.image)
    if (args.is_default !== undefined) formData.append('is_default', String(Boolean(args.is_default)))

    const { data } = await apiClient.patch(`${prefix}/templates/${id}/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  },

  async deleteTemplate(id: number) {
    const { data } = await apiClient.delete(`${prefix}/templates/${id}/`)
    return data
  },

  async verifyByCode(code: string) {
    const { data } = await apiClient.get<VerifyCertificateResponse>(`${prefix}/verify/${encodeURIComponent(code)}/`)
    return data
  },
}
