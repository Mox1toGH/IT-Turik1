import type { JSONContent } from '@tiptap/vue-3'

export interface NewsArticle {
  id: number
  title: string
  content: JSONContent
  created_by: number | null
  created_by_name: string
  created_at: string
  updated_at: string
}
