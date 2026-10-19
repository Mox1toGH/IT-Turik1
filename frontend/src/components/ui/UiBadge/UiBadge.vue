<template>
  <div :class="['badge', `badge--${props.variant}`]"><slot /></div>
</template>

<script setup lang="ts">
export type Variants = 'green' | 'gray' | 'red' | 'orange' | 'primary'

interface Props {
  variant?: Variants
}

const props = withDefaults(defineProps<Props>(), { variant: 'gray' })
</script>

<style scoped>
.badge {
  display: inline-block;
  border-radius: 999px;
  font-size: 0.74rem;
  font-weight: 700;
  padding: 0.2rem 0.5rem;
  border: 1px solid;
}

.badge--green {
  border-color: var(--success);
  background: var(--success-soft);
  color: var(--success);
}

.badge--primary {
  border-color: var(--primary);
  background: var(--primary-soft);
  color: var(--primary);
}

.badge--gray {
  border-color: var(--border-soft);
  background: var(--subtle);
  color: var(--muted-foreground);
}

.badge--red {
  border-color: var(--destructive);
  background: var(--destructive-soft);
  color: var(--destructive);
}

.badge--orange {
  border-color: var(--warning);
  background: color-mix(in srgb, var(--warning) 10%, transparent);
  color: var(--foreground);
}
</style>
