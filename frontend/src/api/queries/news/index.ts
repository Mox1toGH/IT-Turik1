import type { ApiError } from '@/api/errors'
import { $api } from '@/api/services'
import type {
  CreateNewsArgs,
  CreateNewsResponse,
  DeleteNewsArgs,
  GetNewsResponse,
  UpdateNewsArgs,
  UpdateNewsResponse,
} from '@/api/services/news/types'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import type { AxiosError } from 'axios'
import type { MutationConfig, QueryConfig } from '../types'
import { newsKeys } from '../keys'

export const useNewsList = (config?: QueryConfig<GetNewsResponse>) => {
  return useQuery<GetNewsResponse, AxiosError<ApiError>>({
    queryKey: newsKeys.list(),
    queryFn: $api.news.getNews,
    ...config,
  })
}

export const useCreateNews = (
  config?: MutationConfig<
    CreateNewsResponse,
    AxiosError<ApiError<keyof CreateNewsArgs['body']>>,
    CreateNewsArgs
  >,
) => {
  const queryClient = useQueryClient()
  return useMutation<
    CreateNewsResponse,
    AxiosError<ApiError<keyof CreateNewsArgs['body']>>,
    CreateNewsArgs
  >({
    mutationFn: $api.news.createNews,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: newsKeys.list() })
    },
    ...config,
  })
}

export const useUpdateNews = (
  config?: MutationConfig<
    UpdateNewsResponse,
    AxiosError<ApiError<keyof CreateNewsArgs['body']>>,
    UpdateNewsArgs
  >,
) => {
  const queryClient = useQueryClient()
  return useMutation<
    UpdateNewsResponse,
    AxiosError<ApiError<keyof CreateNewsArgs['body']>>,
    UpdateNewsArgs
  >({
    mutationFn: $api.news.updateNews,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: newsKeys.list() })
    },
    ...config,
  })
}

export const useDeleteNews = (
  config?: MutationConfig<unknown, AxiosError<ApiError>, DeleteNewsArgs>,
) => {
  const queryClient = useQueryClient()
  return useMutation<unknown, AxiosError<ApiError>, DeleteNewsArgs>({
    mutationFn: $api.news.deleteNews,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: newsKeys.list() })
    },
    ...config,
  })
}

