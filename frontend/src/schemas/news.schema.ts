import { tiptapJsonToText } from '@/lib/utils'
import * as v from 'valibot'

function tiptapJsonMinLength(min: number, message: string) {
  return v.pipe(
    v.unknown(),
    v.check((value) => tiptapJsonToText(value).length >= min, message),
  )
}

export const CreateNewsSchema = v.object({
  title: v.pipe(v.string(), v.minLength(3, 'Title must be at least 3 characters long')),
  content: tiptapJsonMinLength(20, 'Content must be at least 20 characters long'),
})

