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
            :aria-pressed="editor?.isActive('bold') ?? false"
            @click="toggleUnderline"
            :class="{ 'is-active': editor?.isActive('underline') }"
          >
            <underline-icon />
          </ui-button>
          <ui-button
            size="sm"
            variant="secondary"
            :disabled="!editor"
            :aria-pressed="editor?.isActive('bold') ?? false"
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
        </div>
      </ui-card>

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
import UnderlineIcon from '@/icons/typography/UnderlineIcon.vue'
import HighlightIcon from '@/icons/typography/HighlightIcon.vue'
import Highlight from '@tiptap/extension-highlight'

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

const addTextComputed = computed(() => props.addText || `Add ${props.title.toLowerCase()}`)
const editTextComputed = computed(() => props.editText || `Edit ${props.title.toLowerCase()}`)

const hasValue = computed(() => tiptapJsonToText(modelValue.value).length > 0)

const editor = useEditor({
  extensions: [StarterKit, Highlight],
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
  isOpen.value = true
}

function handleClose() {
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
  editor.value?.chain().focus().toggleHighlight({ color: '#8ce99a' }).run()
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
</style>
