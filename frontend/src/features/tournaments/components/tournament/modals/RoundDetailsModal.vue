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
        <ui-button
          variant="secondary"
          :class="['sections-btn', { active: activeSection === 'description' }]"
          @click="setActiveSection('description')"
          >Description</ui-button
        >
        <ui-button
          variant="secondary"
          :class="['sections-btn', { active: activeSection === 'tech_requirements' }]"
          @click="setActiveSection('tech_requirements')"
          >Technical Requirements</ui-button
        >
        <ui-button
          variant="secondary"
          :class="['sections-btn', { active: activeSection === 'must_have' }]"
          @click="setActiveSection('must_have')"
          >Must Have</ui-button
        >
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
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiModal from '@/components/ui/UiModal.vue'
import StarterKit from '@tiptap/starter-kit'
import { EditorContent, useEditor, type JSONContent } from '@tiptap/vue-3'
import { ref, watch } from 'vue'

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
  extensions: [StarterKit],
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
  extensions: [StarterKit],
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
  extensions: [StarterKit],
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
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 10px;
}

.sections-btn.active {
  background: var(--primary);
  color: var(--primary-foreground);
}

.editor-card {
  overflow-y: auto;
  max-height: 450px;
  background: var(--accent);
}
</style>
