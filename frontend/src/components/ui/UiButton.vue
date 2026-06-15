<template>
  <component
    :is="props.asLink ? RouterLink : 'button'"
    :to="props.asLink ? props.to : undefined"
    :type="props.asLink ? undefined : 'button'"
    :class="['btn', variantClass, sizeClass]"
    v-bind="$attrs"
  >
    <slot />
  </component>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

export type Variant = 'default' | 'secondary' | 'ghost' | 'danger' | 'warning'

export type Size = 'xs' | 'sm' | 'md' | 'lg'

type Props = {
  asLink?: boolean
  to?: string
  variant?: Variant
  size?: Size
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  asLink: false,
  size: 'md',
})

const variants: Record<Variant, string> = {
  default: 'primary-btn',
  secondary: 'secondary-btn',
  ghost: 'ghost-btn',
  danger: 'danger-btn',
  warning: 'warning-btn',
}

const sizes: Record<Size, string> = {
  xs: 'btn-xs',
  sm: 'btn-sm',
  md: 'btn-md',
  lg: 'btn-lg',
}

const variantClass = computed(() => variants[props.variant])
const sizeClass = computed(() => sizes[props.size])
</script>

<style scoped>
.btn-sm {
  padding: 0.45rem 0.7rem;
  font-size: 0.85rem !important;
}

.btn-md {
  padding: 0.7rem 1rem;
  font-size: 1rem !important;
}

.btn-lg {
  padding: 0.9rem 1.35rem;
  font-size: 1.1rem !important;
}

.btn {
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 0;
  gap: 0.4rem;
  font: inherit;
  font-weight: 700;
  border-radius: var(--radius);
  background: var(--secondary);
  color: var(--secondary-foreground);
  cursor: pointer;
  outline: none;
  transition:
    background 0.2s ease,
    color 0.2s ease,
    border-color 0.2s ease,
    opacity 0.2s ease,
    box-shadow 0.2s ease;
}

.btn:focus {
  box-shadow: 0 0 0 3px var(--ring);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.primary-btn {
  border: none;
  color: var(--primary-foreground);
  background: var(--primary);
}

.primary-btn:hover {
  border: none;
  background: var(--primary);
  opacity: 0.75;
}

.secondary-btn {
  background: var(--secondary);
  color: var(--secondary-foreground);
}

.secondary-btn:hover {
  background: color-mix(in oklab, var(--secondary) 70%, transparent);
}

.ghost-btn {
  border: 1px solid;
  background: color-mix(in oklab, var(--primary) 10%, transparent);
  color: var(--foreground);
  border-color: var(--primary);
}

.ghost-btn:hover {
  background: color-mix(in oklab, var(--primary) 20%, transparent);
}

.danger-btn {
  border: 1px solid;
  background: color-mix(in oklab, var(--destructive) 10%, transparent);
  color: var(--destructive);
  border-radius: 12px;
}

.danger-btn:focus {
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--destructive) 20%, transparent);
}

.danger-btn:hover {
  background: color-mix(in oklab, var(--destructive) 20%, transparent);
}

.warning-btn {
  border: 1px solid;
  background: color-mix(in oklab, var(--warning) 10%, transparent);
  color: var(--warning);
}

.warning-btn:focus {
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--warning) 20%, transparent);
}

.warning-btn:hover {
  background: color-mix(in oklab, var(--warning) 20%, transparent);
}
</style>
