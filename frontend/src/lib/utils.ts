import type { JSONContent } from '@tiptap/vue-3'

export function truncateText(text: string, maxLength: number) {
  if (typeof text !== 'string') return
  if (text.length > maxLength) return text.slice(0, maxLength) + '...'
  return text
}

function stripHtml(value: string) {
  return value
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

export function tiptapJsonToText(value: unknown): string {
  if (!value) return ''

  if (typeof value === 'string') {
    return stripHtml(value)
  }

  if (typeof value !== 'object') return ''

  const parts: string[] = []

  const walk = (node: JSONContent) => {
    if (!node || typeof node !== 'object') return

    if (node.type === 'text' && typeof node.text === 'string') {
      parts.push(node.text)
    }

    if (Array.isArray(node.content)) {
      node.content.forEach(walk)
    }
  }

  walk(value)

  return parts.join(' ').replace(/\s+/g, ' ').trim()
}
