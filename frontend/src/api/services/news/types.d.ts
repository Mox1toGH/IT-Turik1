import type { NewsArticle, NewsId } from '@/api/dbTypes'

export interface GetNewsArgs {
  page?: number
  pageSize?: number
}

export interface PaginatedNewsResponse {
  count: number
  next: string | null
  previous: string | null
  results: NewsArticle[]
}

export type GetNewsResponse = PaginatedNewsResponse

export type CreateNewsBody = Pick<NewsArticle, 'title' | 'content'>
export interface CreateNewsArgs {
  body: CreateNewsBody
}
export type CreateNewsResponse = NewsArticle

export interface UpdateNewsArgs {
  id: NewsId
  body: Partial<CreateNewsBody>
}
export type UpdateNewsResponse = NewsArticle

export interface DeleteNewsArgs {
  id: NewsId
}
