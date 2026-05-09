import type { NewsArticle, NewsId } from '@/api/dbTypes'

export interface GetNewsArgs {}
export type GetNewsResponse = NewsArticle[]

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

