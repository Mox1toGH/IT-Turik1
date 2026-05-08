import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import { toValue, type MaybeRefOrGetter } from 'vue'
import type { AxiosError } from 'axios'
import { $api } from '@/api/services'
import { certificateKeys } from '../keys'
import type { QueryConfig } from '../types'
import type { ApiError } from '@/api/errors'
import type {
  GetCertificatesResponse,
  GetCertificateTemplatesResponse,
  PaginatedResponse,
  VerifyCertificateResponse,
} from '@/api/services/certificates/types'

export const useMyCertificates = (
  args: { page?: MaybeRefOrGetter<number>; pageSize?: MaybeRefOrGetter<number> } = {},
  config?: QueryConfig<PaginatedResponse<GetCertificatesResponse>>,
) => {
  return useQuery<PaginatedResponse<GetCertificatesResponse>, AxiosError<ApiError>>({
    queryKey: ['my-certificates', args.page ?? 1, args.pageSize ?? 6],
    queryFn: () =>
      $api.certificates.getMyCertificates({
        page: toValue(args.page) ?? 1,
        pageSize: toValue(args.pageSize) ?? 6,
      }),
    ...config,
  })
}

export const useCertificates = (
  args: { page?: MaybeRefOrGetter<number>; pageSize?: MaybeRefOrGetter<number> } = {},
  config?: QueryConfig<PaginatedResponse<GetCertificatesResponse>>,
) => {
  return useQuery<PaginatedResponse<GetCertificatesResponse>, AxiosError<ApiError>>({
    queryKey: ['certificates', args.page ?? 1, args.pageSize ?? 20],
    queryFn: () =>
      $api.certificates.getCertificates({
        page: toValue(args.page) ?? 1,
        pageSize: toValue(args.pageSize) ?? 20,
      }),
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
      queryClient.invalidateQueries({ queryKey: ['certificates'] })
      queryClient.invalidateQueries({ queryKey: ['my-certificates'] })
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
