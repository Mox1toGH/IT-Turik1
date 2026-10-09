<template>
  <ui-button variant="secondary" @click="openModal">
    {{ hasValue ? editTextComputed : addTextComputed }}
  </ui-button>

  <ui-modal
    v-model="isOpen"
    :maxWidth="props.maxWidth"
    :close-on-backdrop="false"
    @close="handleClose"
  >
    <template #title>
      <h2>{{ title }}</h2>
    </template>

    <div class="editor-shell">
      <ui-card>
        <div class="toolbar" role="toolbar" aria-label="Text editor toolbar">
          <ui-button
            size="sm"
            variant="secondary"
            :disabled="!editor"
            @click="toggleH1"
            :aria-pressed="editor?.isActive('heading', { level: 1 }) ?? false"
            :class="{ 'is-active': editor?.isActive('heading', { level: 1 }) }"
          >
            <heading1-icon width="20px" height="20" />
          </ui-button>
          <ui-button
            size="sm"
            variant="secondary"
            :disabled="!editor"
            @click="toggleH2"
            :aria-pressed="editor?.isActive('heading', { level: 2 }) ?? false"
            :class="{ 'is-active': editor?.isActive('heading', { level: 2 }) }"
          >
            <heading2-icon width="20px" height="20" />
          </ui-button>
          <ui-button
            size="sm"
            variant="secondary"
            :disabled="!editor"
            @click="toggleBold"
            :aria-pressed="editor?.isActive('bold') ?? false"
            :class="{ 'is-active': editor?.isActive('bold') }"
          >
            <bold-icon width="20" height="20" />
          </ui-button>
          <ui-button
            size="sm"
            variant="secondary"
            :disabled="!editor"
            :aria-pressed="editor?.isActive('underline') ?? false"
            @click="toggleUnderline"
            :class="{ 'is-active': editor?.isActive('underline') }"
          >
            <underline-icon />
          </ui-button>
          <ui-button
            size="sm"
            variant="secondary"
            :disabled="!editor"
            :aria-pressed="editor?.isActive('highlight') ?? false"
            @click="toggleHighlight"
            :class="{ 'is-active': editor?.isActive('highlight') }"
          >
            <highlight-icon />
          </ui-button>
          <ui-button
            size="sm"
            variant="secondary"
            :disabled="!editor"
            @click="toggleItalic"
            :aria-pressed="editor?.isActive('italic') ?? false"
            :class="{ 'is-active': editor?.isActive('italic') }"
          >
            <italic-icon width="20" height="20" />
          </ui-button>
          <ui-button
            size="sm"
            variant="secondary"
            :disabled="!editor"
            @click="toggleBulletList"
            :aria-pressed="editor?.isActive('bulletList') ?? false"
            :class="{ 'is-active': editor?.isActive('bulletList') }"
          >
            <bullet-list-icon width="20px" height="20" />
          </ui-button>
          <ui-button
            size="sm"
            variant="secondary"
            :disabled="!editor"
            @click="toggleOrderedList"
            :aria-pressed="editor?.isActive('orderedList') ?? false"
            :class="{ 'is-active': editor?.isActive('orderedList') }"
          >
            <numeric-list-icon width="20px" height="20" />
          </ui-button>
          <ui-button
            size="sm"
            variant="secondary"
            :disabled="!editor"
            @click="toggleLink"
            :aria-pressed="editor?.isActive('link') ?? false"
            :class="{ 'is-active': editor?.isActive('link') }"
          >
            Link
          </ui-button>
        </div>
      </ui-card>

      <form v-if="isLinkEditorOpen" class="link-editor" @submit.prevent="applyLink">
        <label class="link-field-label">
          Link URL
          <ui-input
            v-model="linkUrl"
            type="text"
            inputmode="url"
            autocomplete="url"
            placeholder="https://example.com"
            :is-invalid="!!linkError"
            @input="linkError = ''"
          />
        </label>
        <p v-if="linkError" class="link-error" role="alert">{{ linkError }}</p>
        <div class="link-editor-actions">
          <ui-button size="sm" type="submit">Apply link</ui-button>
          <ui-button size="sm" variant="secondary" type="button" @click="closeLinkEditor">
            Cancel
          </ui-button>
          <ui-button
            v-if="linkSelection?.wasLink"
            size="sm"
            variant="ghost"
            type="button"
            @click="removeLink"
          >
            Remove link
          </ui-button>
        </div>
      </form>

      <editor-content class="editor" :editor="editor" />
    </div>

    <template #footer>
      <ui-button variant="secondary" @click="cancel">Cancel</ui-button>
      <ui-button @click="save">Save</ui-button>
    </template>
  </ui-modal>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiModal from '@/components/ui/UiModal.vue'
import BoldIcon from '@/icons/typography/BoldIcon.vue'
import BulletListIcon from '@/icons/typography/BulletListIcon.vue'
import Heading1Icon from '@/icons/typography/Heading1Icon.vue'
import Heading2Icon from '@/icons/typography/Heading2Icon.vue'
import ItalicIcon from '@/icons/typography/ItalicIcon.vue'
import NumericListIcon from '@/icons/typography/NumericListIcon.vue'
import StarterKit from '@tiptap/starter-kit'
import type { JSONContent } from '@tiptap/core'
import { EditorContent, useEditor } from '@tiptap/vue-3'
import { computed, ref } from 'vue'
import { tiptapJsonToText } from '@/lib/utils'
import * as v from 'valibot'
import { LinkUrlSchema } from '@/schemas/link.schema'
import UnderlineIcon from '@/icons/typography/UnderlineIcon.vue'
import HighlightIcon from '@/icons/typography/HighlightIcon.vue'
import Highlight from '@tiptap/extension-highlight'
import Link from '@tiptap/extension-link'
import Underline from '@tiptap/extension-underline'

interface Props {
  title: string
  addText?: string
  editText?: string
  ariaLabel?: string
  maxWidth?: string
}

const props = withDefaults(defineProps<Props>(), {
  addText: '',
  editText: '',
  ariaLabel: '',
  maxWidth: '1200px',
})

const emit = defineEmits<{
  (e: 'blur'): void
}>()

const modelValue = defineModel<JSONContent | null>({ default: null })

const isOpen = ref(false)
const draftJson = ref<JSONContent | null>(modelValue.value)
const isLinkEditorOpen = ref(false)
const linkUrl = ref('')
const linkError = ref('')
const linkSelection = ref<{ from: number; to: number; wasLink: boolean } | null>(null)

const addTextComputed = computed(() => props.addText || `Add ${props.title.toLowerCase()}`)
const editTextComputed = computed(() => props.editText || `Edit ${props.title.toLowerCase()}`)

const hasValue = computed(() => tiptapJsonToText(modelValue.value).length > 0)

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
      'aria-label': props.ariaLabel || `${props.title} editor`,
    },
  },
  onUpdate({ editor }) {
    draftJson.value = editor.getJSON()
  },
})

function openModal() {
  draftJson.value = modelValue.value
  editor.value?.commands.setContent(draftJson.value ?? '', { emitUpdate: false })
  closeLinkEditor()
  isOpen.value = true
}

function handleClose() {
  closeLinkEditor()
  isOpen.value = false
  emit('blur')
}

function cancel() {
  handleClose()
  emit('blur')
}

function save() {
  modelValue.value = draftJson.value
  handleClose()
  emit('blur')
}

function toggleBold() {
  editor.value?.chain().focus().toggleBold().run()
}

function toggleItalic() {
  editor.value?.chain().focus().toggleItalic().run()
}

function toggleUnderline() {
  editor.value?.chain().focus().toggleUnderline().run()
}

function toggleHighlight() {
  if (!editor.value) return

  const chain = editor.value.chain().focus()
  if (editor.value.isActive('highlight')) {
    chain.unsetHighlight().run()
    return
  }

  chain.setHighlight({ color: '#8ce99a' }).run()
}

function toggleBulletList() {
  editor.value?.chain().focus().toggleBulletList().run()
}

function toggleOrderedList() {
  editor.value?.chain().focus().toggleOrderedList().run()
}

function toggleH1() {
  editor.value?.chain().focus().toggleHeading({ level: 1 }).run()
}

function toggleH2() {
  editor.value?.chain().focus().toggleHeading({ level: 2 }).run()
}

function toggleLink() {
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

function applyLink() {
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

function removeLink() {
  if (!editor.value || !linkSelection.value?.wasLink) return

  editor.value.chain().focus().extendMarkRange('link').unsetLink().run()
  closeLinkEditor()
}

function closeLinkEditor() {
  isLinkEditorOpen.value = false
  linkError.value = ''
}
</script>

<style scoped>
.editor-shell {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  height: min(70vh, 760px);
  min-height: 420px;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.toolbar button.is-active {
  background: var(--primary);
  color: var(--primary-foreground);
}

.link-editor {
  display: grid;
  gap: 0.55rem;
  padding: 0.75rem;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--background);
  color: var(--foreground);
}

.link-field-label {
  display: grid;
  gap: 0.35rem;
  font-size: 0.84rem;
  font-weight: 600;
}

.link-field-label :deep(input) {
  width: 100%;
}

.link-error {
  margin: 0;
  color: var(--destructive);
  font-size: 0.82rem;
}

.link-editor-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.editor {
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 0.75rem;
  flex: 1 1 auto;
  background: var(--input);
  overflow: auto;
}

.editor :deep(.ProseMirror) {
  outline: none;
  min-height: 100%;
}

.editor :deep(.ProseMirror p) {
  margin: 0.5rem 0;
}

.editor :deep(.ProseMirror h1) {
  font-size: 1.6rem;
  line-height: 1.25;
  margin: 0.9rem 0 0.6rem;
}

.editor :deep(.ProseMirror h2) {
  font-size: 1.25rem;
  line-height: 1.3;
  margin: 0.85rem 0 0.55rem;
}

.editor :deep(.ProseMirror a) {
  color: #1c7ed6;
  text-decoration: underline;
  text-underline-offset: 2px;
  font-weight: 600;
  transition: color 0.2s ease;
}

.editor :deep(.ProseMirror a:hover) {
  color: #1864ab;
}
</style>
