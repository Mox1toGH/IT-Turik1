import StarterKit from '@tiptap/starter-kit'
import type { JSONContent } from '@tiptap/core'
import { useEditor } from '@tiptap/vue-3'
import { ref, toValue, type MaybeRefOrGetter, type Ref } from 'vue'
import * as v from 'valibot'
import { LinkUrlSchema } from '@/schemas/link.schema'
import Highlight from '@tiptap/extension-highlight'
import Link from '@tiptap/extension-link'
import Underline from '@tiptap/extension-underline'

export interface RoundEditorLinkSelection {
  from: number
  to: number
  wasLink: boolean
}

export function useRoundEditor(
  modelValue: Ref<JSONContent | null>,
  options: {
    title: MaybeRefOrGetter<string>
    ariaLabel?: MaybeRefOrGetter<string>
    onBlur?: () => void
  },
) {
  const isOpen = ref<boolean>(false)
  const draftJson = ref<JSONContent | null>(modelValue.value)
  const isLinkEditorOpen = ref<boolean>(false)
  const linkUrl = ref<string>('')
  const linkError = ref<string>('')
  const linkSelection = ref<RoundEditorLinkSelection | null>(null)

  const editor = useEditor({
    extensions: [
      StarterKit,
      Underline,
      Highlight,
      Link.configure({
        openOnClick: true,
        autolink: true,
        defaultProtocol: 'https',
        HTMLAttributes: {
          rel: 'noopener noreferrer nofollow',
          target: '_blank',
        },
      }),
    ],
    content: draftJson.value ?? '',
    editorProps: {
      attributes: {
        class: 'prose',
        'aria-label': toValue(options.ariaLabel) || `${toValue(options.title)} editor`,
      },
    },
    onUpdate({ editor }) {
      draftJson.value = editor.getJSON()
    },
  })

  function openModal(): void {
    draftJson.value = modelValue.value
    editor.value?.commands.setContent(draftJson.value ?? '', { emitUpdate: false })
    closeLinkEditor()
    isOpen.value = true
  }

  function handleClose(): void {
    closeLinkEditor()
    isOpen.value = false
    options.onBlur?.()
  }

  function cancel(): void {
    handleClose()
    options.onBlur?.()
  }

  function save(): void {
    modelValue.value = draftJson.value
    handleClose()
    options.onBlur?.()
  }

  function toggleBold(): void {
    editor.value?.chain().focus().toggleBold().run()
  }

  function toggleItalic(): void {
    editor.value?.chain().focus().toggleItalic().run()
  }

  function toggleUnderline(): void {
    editor.value?.chain().focus().toggleUnderline().run()
  }

  function toggleHighlight(): void {
    if (!editor.value) return
    const chain = editor.value.chain().focus()
    if (editor.value.isActive('highlight')) {
      chain.unsetHighlight().run()
      return
    }
    chain.setHighlight({ color: '#8ce99a' }).run()
  }

  function toggleBulletList(): void {
    editor.value?.chain().focus().toggleBulletList().run()
  }

  function toggleOrderedList(): void {
    editor.value?.chain().focus().toggleOrderedList().run()
  }

  function toggleH1(): void {
    editor.value?.chain().focus().toggleHeading({ level: 1 }).run()
  }

  function toggleH2(): void {
    editor.value?.chain().focus().toggleHeading({ level: 2 }).run()
  }

  function toggleLink(): void {
    if (!editor.value) return
    const { from, to, empty } = editor.value.state.selection
    const wasLink = editor.value.isActive('link')
    linkSelection.value = { from, to, wasLink }
    linkUrl.value = wasLink ? String(editor.value.getAttributes('link').href ?? '') : ''
    linkError.value = !wasLink && empty ? 'Select text in the editor before adding a link.' : ''
    isLinkEditorOpen.value = true
  }

  function validateLinkUrl(value: string): string | null {
    const result = v.safeParse(LinkUrlSchema, value)
    if (!result.success) {
      linkError.value = result.issues.map((issue) => issue.message).join(' ')
      return null
    }
    linkError.value = ''
    return result.output
  }

  function applyLink(): void {
    if (!editor.value || !linkSelection.value) return
    const href = validateLinkUrl(linkUrl.value)
    if (!href) return
    const { from, to, wasLink } = linkSelection.value
    if (!wasLink && from === to) {
      linkError.value = 'Select text in the editor before adding a link.'
      return
    }
    const chain = editor.value.chain().focus()
    if (wasLink) chain.extendMarkRange('link')
    else chain.setTextSelection({ from, to })
    chain.setLink({ href }).run()
    closeLinkEditor()
  }

  function removeLink(): void {
    if (!editor.value || !linkSelection.value?.wasLink) return
    editor.value.chain().focus().extendMarkRange('link').unsetLink().run()
    closeLinkEditor()
  }

  function closeLinkEditor(): void {
    isLinkEditorOpen.value = false
    linkError.value = ''
  }

  return {
    editor,
    isOpen,
    draftJson,
    isLinkEditorOpen,
    linkUrl,
    linkError,
    linkSelection,
    openModal,
    handleClose,
    cancel,
    save,
    toggleBold,
    toggleItalic,
    toggleUnderline,
    toggleHighlight,
    toggleBulletList,
    toggleOrderedList,
    toggleH1,
    toggleH2,
    toggleLink,
    validateLinkUrl,
    applyLink,
    removeLink,
    closeLinkEditor,
  }
}
