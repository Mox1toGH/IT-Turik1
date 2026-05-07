import type { ApiError } from '@/api'
import type { UseMutationOptions, UseQueryOptions } from '@tanstack/vue-query'
import type { AxiosError } from 'axios'

export type QueryConfig<Data = unknown, Error = AxiosError<ApiError>> = UseQueryOptions<Data, Error>

export type MutationConfig<
  Data = unknown,
  Error = AxiosError<ApiError>,
  Variables = void,
> = UseMutationOptions<Data, Error, Variables>

export type MaybeRefArgs<T> = {
  [K in keyof T]: MaybeRef<T[K]>
}
