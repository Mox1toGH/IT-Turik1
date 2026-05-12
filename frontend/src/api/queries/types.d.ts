import type { ApiError } from '@/api'
import type { UseMutationOptions, UseQueryOptions } from '@tanstack/vue-query'
import type { AxiosError } from 'axios'

// queryKey and queryFn are required in UseQueryOptions, but in our hooks they are always
// defined internally — so we make them optional via Partial<Pick> to avoid
// forcing consumers to pass them, while keeping full TS autocomplete for all other options.
export type QueryConfig<Data = unknown, Error = AxiosError<ApiError>> = Partial<
  UseQueryOptions<Data, Error>
>

// Same as described above
export type MutationConfig<
  Data = unknown,
  Error = AxiosError<ApiError>,
  Variables = void,
> = Partial<UseMutationOptions<Data, Error, Variables>>

export type MaybeRefArgs<T> = {
  [K in keyof T]: MaybeRef<T[K]>
}
