import { mergeAttributes } from '@tiptap/core'
import Link from '@tiptap/extension-link'
import { getSafeRichTextHref } from '@/schemas/link.schema'

const safeLinkRel = 'noopener noreferrer nofollow'

export const SafeTiptapLink = Link.extend({
  renderHTML({ HTMLAttributes }) {
    const href = getSafeRichTextHref(HTMLAttributes.href)
    if (!href) return ['span', {}, 0]

    return [
      'a',
      mergeAttributes(this.options.HTMLAttributes, HTMLAttributes, {
        href,
        target: '_blank',
        rel: safeLinkRel,
      }),
      0,
    ]
  },
}).configure({
  openOnClick: true,
  autolink: true,
  defaultProtocol: 'https',
  isAllowedUri: (url) => getSafeRichTextHref(url) !== null,
  HTMLAttributes: {
    rel: safeLinkRel,
    target: '_blank',
  },
})
