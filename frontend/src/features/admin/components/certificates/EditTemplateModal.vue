<template>
  <ui-modal v-model="open">
    <template #title><h3 class="panel-title">Edit Template</h3></template>
    <form class="template-form" @submit.prevent="$emit('submit')">
      <div class="form-item"><label class="form-label">Template name</label><ui-input v-model="localForm.name" required placeholder="Summer Cup 2026" /></div>
      <div class="form-item">
        <label class="form-label">Image (optional)</label>
        <input class="file-input" type="file" accept="image/*" @change="$emit('file-change', $event)" />
        <p class="panel-note">Leave empty to keep current image</p>
      </div>
      <label class="check"><input v-model="localForm.is_default" type="checkbox" />Make default template</label>
      <ui-button type="submit" :disabled="isUpdating" class="submit">{{ isUpdating ? 'Saving...' : 'Save Changes' }}</ui-button>
    </form>
  </ui-modal>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import UiModal from '@/components/ui/UiModal.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiButton from '@/components/ui/UiButton.vue'

const props = defineProps<{ modelValue: boolean; form: { name: string; file: File | null; is_default: boolean }; isUpdating: boolean }>()
const emit = defineEmits<{ (e: 'update:modelValue', value: boolean): void; (e: 'update:form', value: typeof props.form): void; (e: 'file-change', event: Event): void; (e: 'submit'): void }>()

const open = computed({ get: () => props.modelValue, set: (v) => emit('update:modelValue', v) })
const localForm = computed({ get: () => props.form, set: (v) => emit('update:form', v) })
</script>

<style scoped>
.panel-title { margin: 0; font-size: 1rem; }
.panel-note { font-size: 0.8rem; color: var(--color-gray-500); }
.template-form { display: grid; gap: 0.65rem; }
.form-item { display: grid; gap: 0.4rem; }
.form-label { font-size: 0.85rem; font-weight: 600; }
.submit { width: fit-content; }
.file-input { border: 1px solid var(--line-soft); border-radius: 12px; padding: 0.6rem 0.8rem; background: var(--background); color: var(--foreground); font-size: 0.95rem; cursor: pointer; transition: all 0.2s ease; }
.file-input:hover { border-color: var(--primary); }
.file-input::file-selector-button { background: var(--primary); color: var(--primary-foreground); border: none; border-radius: 8px; padding: 0.4rem 0.8rem; margin-right: 1rem; font-weight: 600; cursor: pointer; transition: opacity 0.2s; }
.file-input::file-selector-button:hover { opacity: 0.85; }
.check { display: flex; align-items: center; gap: 0.55rem; font-size: 0.9rem; }
</style>
