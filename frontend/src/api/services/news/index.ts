import { apiClient } from '@/api/client'
import type {
  CreateNewsArgs,
  CreateNewsResponse,
  DeleteNewsArgs,
  GetNewsArgs,
  GetNewsResponse,
  UpdateNewsArgs,
  UpdateNewsResponse,
} from './types'

const prefix = '/api/news'

export const newsService = {
  async getNews(args?: GetNewsArgs) {
    const page = args?.page ?? 1
    const pageSize = args?.pageSize ?? 10
    const { data } = await apiClient.get<GetNewsResponse | GetNewsResponse['results']>(`${prefix}/`, {
      params: { page, page_size: pageSize },
    })

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

  async createNews(args: CreateNewsArgs) {
    const { data } = await apiClient.post<CreateNewsResponse>(`${prefix}/`, args.body)
    return data
  },

  async updateNews(args: UpdateNewsArgs) {
    const { data } = await apiClient.patch<UpdateNewsResponse>(`${prefix}/${args.id}/`, args.body)
    return data
  },

  async deleteNews(args: DeleteNewsArgs) {
    const { data } = await apiClient.delete(`${prefix}/${args.id}/`)
    return data
  },
}
