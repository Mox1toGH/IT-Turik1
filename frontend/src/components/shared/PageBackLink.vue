<template>
  <div class="page-back-link-row">
    <ui-button
      v-if="to"
      as-link
      :to="to"
      variant="link"
      size="sm"
      class="page-back-link"
    >
      <ArrowLeft :size="17" aria-hidden="true" />
      {{ label }}
    </ui-button>
    <ui-button v-else variant="link" size="sm" class="page-back-link" @click="$emit('back')">
      <ArrowLeft :size="17" aria-hidden="true" />
      {{ label }}
    </ui-button>
  </div>
</template>

<script setup lang="ts">
import { ArrowLeft } from 'lucide-vue-next'
import UiButton from '@/components/ui/UiButton'

defineProps<{
  label: string
  to?: string
}>()

defineEmits<{
  back: []
}>()
</script>

<style scoped>
.page-back-link-row {
  display: flex;
  align-items: center;
  width: 100%;
  padding-bottom: 0.75rem;
  margin-bottom: 0.75rem;
  border-bottom: 1px solid var(--border);
}

.page-back-link {
  display: inline-flex;
  width: max-content;
  min-height: 2rem;
  align-items: center;
  gap: 0.45rem;
  color: var(--primary);
  font-size: var(--text-sm);
  font-weight: 750;
  text-decoration-thickness: 1.5px;
  text-underline-offset: 0.2em;
}

.page-back-link:hover {
  color: var(--foreground);
}

.page-back-link:focus-visible {
  outline: 2px solid var(--ring);
  outline-offset: 3px;
}
</style>
