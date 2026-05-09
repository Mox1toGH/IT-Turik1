import { apiClient } from '@/api/client'
import type {
  CreateNewsArgs,
  CreateNewsResponse,
  DeleteNewsArgs,
  GetNewsResponse,
  UpdateNewsArgs,
  UpdateNewsResponse,
} from './types'

const prefix = '/api/news'

export const newsService = {
  async getNews() {
    const { data } = await apiClient.get<GetNewsResponse>(`${prefix}/`)
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

