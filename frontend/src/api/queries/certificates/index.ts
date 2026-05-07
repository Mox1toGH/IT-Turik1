import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import type { AxiosError } from 'axios'
import { $api } from '@/api/services'
import { certificateKeys } from '../keys'
import type { QueryConfig } from '../types'
import type { ApiError } from '@/api/errors'
import type {
  GetCertificatesResponse,
  GetCertificateTemplatesResponse,
  VerifyCertificateResponse,
} from '@/api/services/certificates/types'

export const useMyCertificates = (config?: QueryConfig<GetCertificatesResponse>) => {
  return useQuery<GetCertificatesResponse, AxiosError<ApiError>>({
    queryKey: certificateKeys.myCertificates(),
    queryFn: $api.certificates.getMyCertificates,
    ...config,
  })
}

export const useCertificates = (config?: QueryConfig<GetCertificatesResponse>) => {
  return useQuery<GetCertificatesResponse, AxiosError<ApiError>>({
    queryKey: certificateKeys.allCertificates(),
    queryFn: $api.certificates.getCertificates,
    ...config,
  })
}

export const useCertificateTemplates = (config?: QueryConfig<GetCertificateTemplatesResponse>) => {
  return useQuery<GetCertificateTemplatesResponse, AxiosError<ApiError>>({
    queryKey: certificateKeys.templates(),
    queryFn: $api.certificates.getTemplates,
    ...config,
  })
}

export const useCreateCertificate = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: $api.certificates.createCertificate,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: certificateKeys.allCertificates() })
      queryClient.invalidateQueries({ queryKey: certificateKeys.myCertificates() })
    },
  })
}

export const useUploadCertificateTemplate = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: $api.certificates.uploadTemplate,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: certificateKeys.templates() })
    },
  })
}

export const useVerifyCertificate = (code: string, enabled = false) => {
  return useQuery<VerifyCertificateResponse, AxiosError<ApiError>>({
    queryKey: certificateKeys.verify(code),
    queryFn: () => $api.certificates.verifyByCode(code),
    enabled,
  })
}
