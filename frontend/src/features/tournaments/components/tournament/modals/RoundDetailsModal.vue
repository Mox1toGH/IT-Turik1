<template>
  <ui-modal
    :modelValue="props.modelValue"
    @update:modelValue="emit('update:modelValue', $event)"
    scrollable
    maxWidth="1100px"
    @close="handleClose"
  >
    <template #title>
      <h2>{{ props.title }}</h2>
    </template>

    <div>
      <div class="sections">
        <div
          variant="secondary"
          :class="['sections-btn', { active: activeSection === 'description' }]"
          @click="setActiveSection('description')"
        >
          Description
        </div>
        <div
          variant="secondary"
          :class="['sections-btn', { active: activeSection === 'tech_requirements' }]"
          @click="setActiveSection('tech_requirements')"
        >
          Technical Requirements
        </div>
        <div
          variant="secondary"
          :class="['sections-btn', { active: activeSection === 'must_have' }]"
          @click="setActiveSection('must_have')"
        >
          Must Have
        </div>
      </div>

      <div>
        <ui-card v-if="activeSection === 'description'" class="editor-card">
          <editor-content class="details-editor" :editor="descriptionEditor" />
        </ui-card>

        <ui-card v-if="activeSection === 'tech_requirements'" class="editor-card">
          <editor-content class="details-editor" :editor="requirementsEditor" />
        </ui-card>

        <ui-card v-if="activeSection === 'must_have'" class="editor-card">
          <editor-content class="details-editor" :editor="mustHaveEditor" />
        </ui-card>
      </div>
    </div>
  </ui-modal>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard.vue'
import UiModal from '@/components/ui/UiModal.vue'
import StarterKit from '@tiptap/starter-kit'
import { EditorContent, useEditor, type JSONContent } from '@tiptap/vue-3'
import { ref, watch } from 'vue'
import Highlight from '@tiptap/extension-highlight'

interface Props {
  modelValue: boolean
  title: string
  description: JSONContent
  technicalRequirements: JSONContent
  mustHave: JSONContent
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
}>()

type Section = 'description' | 'must_have' | 'tech_requirements'
const activeSection = ref<Section>('description')

const setActiveSection = (section: Section) => {
  activeSection.value = section
}

const descriptionEditor = useEditor({
  extensions: [StarterKit, Highlight],
  content: props.description,
  editable: false,
  editorProps: {
    attributes: {
      class: 'prose',
      'aria-readonly': 'true',
    },
  },
})

const requirementsEditor = useEditor({
  extensions: [StarterKit, Highlight],
  content: props.technicalRequirements,
  editable: false,
  editorProps: {
    attributes: {
      class: 'prose',
      'aria-readonly': 'true',
    },
  },
})

const mustHaveEditor = useEditor({
  extensions: [StarterKit, Highlight],
  content: props.mustHave,
  editable: false,
  editorProps: {
    attributes: {
      class: 'prose',
      'aria-readonly': 'true',
    },
  },
})

watch(
  () => props.description,
  (value) => {
    descriptionEditor.value?.commands.setContent(value)
  },
)

watch(
  () => props.technicalRequirements,
  (value) => {
    requirementsEditor.value?.commands.setContent(value)
  },
)

watch(
  () => props.mustHave,
  (value) => {
    mustHaveEditor.value?.commands.setContent(value)
  },
)

const handleClose = () => {
  activeSection.value = 'description'
  emit('update:modelValue', false)
}
</script>

<style scoped>
.sections {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  border-bottom: 2px solid var(--border);
  margin-bottom: 1rem;
}

.sections-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.4rem;
  padding-bottom: 0.8rem;
  border-bottom: 2px solid transparent;
  font-weight: 600;
  transition: all 0.2s ease;
}

.sections-btn:hover {
  cursor: pointer;
}

.sections-btn.active,
.sections-btn:hover {
  border-bottom: 2px solid var(--primary);
  color: var(--primary);
}

.editor-card {
  overflow-y: auto;
  max-height: 450px;
  background: var(--accent);
}
</style>
