<template>
  <ui-button variant="secondary" @click="openModal">
    {{ hasValue ? editTextComputed : addTextComputed }}
  </ui-button>

  <ui-modal v-model="isOpen" :maxWidth="props.maxWidth" @close="handleClose">
    <template #title>
      <h2>{{ title }}</h2>
    </template>

    <div class="editor-shell">
      <div class="toolbar" role="toolbar" aria-label="Text editor toolbar">
        <ui-button
          size="sm"
          variant="secondary"
          :disabled="!editor"
          @click="toggleH1"
          :aria-pressed="editor?.isActive('heading', { level: 1 }) ?? false"
          :class="{ 'is-active': editor?.isActive('heading', { level: 1 }) }"
        >
          <Heading1 :size="20" />
        </ui-button>
        <ui-button
          size="sm"
          variant="secondary"
          :disabled="!editor"
          @click="toggleH2"
          :aria-pressed="editor?.isActive('heading', { level: 2 }) ?? false"
          :class="{ 'is-active': editor?.isActive('heading', { level: 2 }) }"
        >
          <Heading2 :size="20" />
        </ui-button>
        <ui-button
          size="sm"
          variant="secondary"
          :disabled="!editor"
          @click="toggleBold"
          :aria-pressed="editor?.isActive('bold') ?? false"
          :class="{ 'is-active': editor?.isActive('bold') }"
        >
          <Bold :size="20" />
        </ui-button>
        <ui-button
          size="sm"
          variant="secondary"
          :disabled="!editor"
          :aria-pressed="editor?.isActive('underline') ?? false"
          @click="toggleUnderline"
          :class="{ 'is-active': editor?.isActive('underline') }"
        >
          <Underline :size="16" />
        </ui-button>
        <ui-button
          size="sm"
          variant="secondary"
          :disabled="!editor"
          :aria-pressed="editor?.isActive('highlight') ?? false"
          @click="toggleHighlight"
          :class="{ 'is-active': editor?.isActive('highlight') }"
        >
          <Highlighter :size="16" />
        </ui-button>
        <ui-button
          size="sm"
          variant="secondary"
          :disabled="!editor"
          @click="toggleItalic"
          :aria-pressed="editor?.isActive('italic') ?? false"
          :class="{ 'is-active': editor?.isActive('italic') }"
        >
          <Italic :size="20" />
        </ui-button>
        <ui-button
          size="sm"
          variant="secondary"
          :disabled="!editor"
          @click="toggleBulletList"
          :aria-pressed="editor?.isActive('bulletList') ?? false"
          :class="{ 'is-active': editor?.isActive('bulletList') }"
        >
          <List :size="20" />
        </ui-button>
        <ui-button
          size="sm"
          variant="secondary"
          :disabled="!editor"
          @click="toggleOrderedList"
          :aria-pressed="editor?.isActive('orderedList') ?? false"
          :class="{ 'is-active': editor?.isActive('orderedList') }"
        >
          <ListOrdered :size="20" />
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
import UiButton from '@/components/ui/UiButton'
import UiInput from '@/components/ui/UiInput'
import UiModal from '@/components/ui/UiModal'
import type { JSONContent } from '@tiptap/core'
import {
  Bold,
  Heading1,
  Heading2,
  Highlighter,
  Italic,
  List,
  ListOrdered,
  Underline,
} from 'lucide-vue-next'
import { EditorContent } from '@tiptap/vue-3'
import { computed } from 'vue'
import { tiptapJsonToText } from '@/lib/utils'
import { useRichTextEditor } from '@/composables/useRichTextEditor'

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

const {
  editor,
  isOpen,
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
  applyLink,
  removeLink,
  closeLinkEditor,
} = useRichTextEditor(modelValue, {
  title: () => props.title,
  ariaLabel: () => props.ariaLabel,
  onBlur: () => emit('blur'),
})

const addTextComputed = computed(() => props.addText || `Add ${props.title.toLowerCase()}`)
const editTextComputed = computed(() => props.editText || `Edit ${props.title.toLowerCase()}`)

const hasValue = computed(() => tiptapJsonToText(modelValue.value).length > 0)
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
  padding: 0.5rem;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--subtle);
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
  background: var(--card);
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
  color: var(--primary);
  text-decoration: underline;
  text-underline-offset: 2px;
  font-weight: 600;
}

.editor :deep(.ProseMirror a:hover) {
  color: color-mix(in srgb, var(--primary) 80%, var(--foreground));
}
</style>
