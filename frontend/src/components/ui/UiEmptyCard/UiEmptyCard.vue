<template>
  <ui-card class="empty-card" :class="{ 'empty-card--start': align === 'start' }" role="status">
    <slot name="icon" />
    <div class="empty-card-copy">
      <h3 v-if="title">{{ title }}</h3>
      <p v-if="message">{{ message }}</p>
      <slot />
    </div>
    <div v-if="$slots.actions" class="empty-card-actions">
      <slot name="actions" />
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard'

withDefaults(
  defineProps<{
    title?: string
    message?: string
    align?: 'center' | 'start'
  }>(),
  { align: 'center' },
)
</script>

<style scoped>
.empty-card {
  display: grid;
  justify-items: center;
  gap: 0.55rem;
  min-width: 0;
  padding: 1.5rem;
  border-style: dashed;
  border-color: var(--border);
  background: var(--subtle);
  text-align: center;
}

.empty-card :deep(.card-body) {
  align-items: center;
}

.empty-card-copy {
  display: grid;
  justify-items: center;
  gap: 0.35rem;
  min-width: 0;
}

.empty-card-copy h3,
.empty-card-copy p {
  margin: 0;
}

.empty-card-copy h3 {
  color: var(--foreground);
  font-size: var(--text-base);
  font-weight: 800;
}

.empty-card-copy p {
  color: var(--muted-foreground);
  font-size: var(--text-sm);
  overflow-wrap: anywhere;
}

.empty-card-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.5rem;
}

.empty-card--start,
.empty-card--start .empty-card-copy {
  justify-items: start;
  text-align: left;
}

.empty-card--start :deep(.card-body) {
  align-items: flex-start;
}

.empty-card--start .empty-card-actions {
  justify-content: flex-start;
}
</style>
