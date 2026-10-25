<template>
  <ui-card class="management-action-card" :class="{ 'management-action-card--danger': danger }">
    <div class="management-action-copy">
      <h3>{{ title }}</h3>
      <p class="text-muted">{{ description }}</p>
    </div>
    <div class="management-action-control">
      <slot name="action" />
    </div>
    <slot />
  </ui-card>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard'

defineProps<{
  title: string
  description: string
  danger?: boolean
}>()
</script>

<style scoped>
.management-action-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 1rem;
  min-width: 0;
  border-color: var(--line-soft);
  background: var(--card);
}

.management-action-copy {
  min-width: 0;
}

.management-action-copy h3 {
  margin: 0;
  color: var(--foreground);
  font-size: 1rem;
  font-weight: 800;
}

.management-action-copy p {
  margin: 0.3rem 0 0;
}

.management-action-control {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  width: 100%;
}

.management-action-card--danger {
  border-color: var(--destructive-ring);
  background: var(--destructive-soft);
}

.management-action-card--danger .management-action-copy h3 {
  color: var(--destructive);
}

</style>
