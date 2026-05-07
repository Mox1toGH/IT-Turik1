import { useQuery } from '@tanstack/vue-query'
import type { AxiosError } from 'axios'
import { $api } from '@/api/services'
import { certificateKeys } from '../keys'
import type { QueryConfig } from '../types'
import type { ApiError } from '@/api/errors'
import type { GetCertificatesResponse } from '@/api/services/certificates/types'

export const useMyCertificates = (config?: QueryConfig<GetCertificatesResponse>) => {
  return useQuery<GetCertificatesResponse, AxiosError<ApiError>>({
    queryKey: certificateKeys.myCertificates(),
    queryFn: $api.certificates.getMyCertificates,
    ...config,
  })
}
