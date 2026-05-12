import type { ApiError } from '@/api/errors'
import { $api } from '@/api/services'
import type {
  CreateNewsArgs,
  CreateNewsResponse,
  GetNewsArgs,
  DeleteNewsArgs,
  GetNewsResponse,
  UpdateNewsArgs,
  UpdateNewsResponse,
} from '@/api/services/news/types'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import type { AxiosError } from 'axios'
import type { MutationConfig, QueryConfig } from '../types'
import { newsKeys } from '../keys'
import { computed, type Ref, unref } from 'vue'

export const useNewsList = (
  args?: { page?: Ref<number> | number; pageSize?: Ref<number> | number },
  config?: QueryConfig<GetNewsResponse>,
) => {
  return useQuery<GetNewsResponse, AxiosError<ApiError>>({
    queryKey: computed(() => newsKeys.list(unref(args?.page ?? 1), unref(args?.pageSize ?? 10))),
    queryFn: () =>
      $api.news.getNews({
        page: unref(args?.page ?? 1),
        pageSize: unref(args?.pageSize ?? 10),
      } as GetNewsArgs),
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
      queryClient.invalidateQueries({ queryKey: newsKeys.lists() })
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
      queryClient.invalidateQueries({ queryKey: newsKeys.lists() })
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
      queryClient.invalidateQueries({ queryKey: newsKeys.lists() })
    },
    ...config,
  })
}
