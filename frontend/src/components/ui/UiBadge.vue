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
  border-color: #0d9412;
  background: #41940d1f;
  color: #22940d;
}

.badge--primary {
  border-color: color-mix(in srgb, var(--primary) 40%, transparent);
  background: color-mix(in srgb, var(--primary) 10%, transparent);
  color: var(--primary);
}

.badge--gray {
  border-color: color-mix(in srgb, var(--border) 40%, transparent);
  background: var(--secondary);
  color: var(--muted-foreground);
}

.badge--red {
  border-color: color-mix(in srgb, var(--destructive) 40%, transparent);
  background: color-mix(in srgb, var(--destructive) 10%, transparent);
  color: var(--destructive);
}

.badge--orange {
  border-color: color-mix(in srgb, var(--warning) 40%, transparent);
  background: color-mix(in srgb, var(--warning) 10%, transparent);
  color: var(--warning);
}
</style>
