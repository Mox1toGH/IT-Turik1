<template>
  <editor-content class="news-content" :editor="editor" />
</template>

<script setup lang="ts">
import Highlight from '@tiptap/extension-highlight'
import Link from '@tiptap/extension-link'
import StarterKit from '@tiptap/starter-kit'
import { EditorContent, useEditor, type JSONContent } from '@tiptap/vue-3'
import { watch } from 'vue'

interface Props {
  content: JSONContent
}

const props = defineProps<Props>()

const editor = useEditor({
  extensions: [
    StarterKit,
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
  content: props.content,
  editable: false,
  editorProps: {
    attributes: {
      class: 'prose',
      'aria-readonly': 'true',
    },
  },
})

watch(
  () => props.content,
  (value) => {
    editor.value?.commands.setContent(value)
  },
)
</script>

<style scoped>
.news-content {
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--card);
  padding: 0.85rem;
}

.news-content :deep(.ProseMirror) {
  outline: none;
}

.news-content :deep(.ProseMirror p) {
  margin: 0.5rem 0;
}

.news-content :deep(.ProseMirror h1) {
  font-size: 1.45rem;
  line-height: 1.2;
  margin: 0.9rem 0 0.6rem;
}

.news-content :deep(.ProseMirror h2) {
  font-size: 1.2rem;
  line-height: 1.25;
  margin: 0.8rem 0 0.55rem;
}

.news-content :deep(.ProseMirror a) {
  color: #1c7ed6;
  text-decoration: underline;
  text-underline-offset: 2px;
  font-weight: 600;
}

.news-content :deep(.ProseMirror a:hover) {
  color: #1864ab;
}
</style>
