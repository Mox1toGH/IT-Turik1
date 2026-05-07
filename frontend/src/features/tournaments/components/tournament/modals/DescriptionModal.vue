<template>
  <ui-modal
    :model-value="props.modelValue"
    @update:model-value="(val) => emit('update:modelValue', val)"
  >
    <template #title>
      <h3>Tournament description</h3>
    </template>

    <p class="text-muted">
      {{ props.description }}
    </p>
  </ui-modal>
</template>

<script setup lang="ts">
import UiModal from '@/components/ui/UiModal.vue'

interface Props {
  modelValue: boolean
  description: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()
</script>
