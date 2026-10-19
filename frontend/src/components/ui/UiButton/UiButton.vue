<template>
  <component
    :is="props.asLink ? RouterLink : 'button'"
    :to="props.asLink ? props.to : undefined"
    :type="props.asLink ? undefined : 'button'"
    :disabled="props.disabled"
    :class="['btn', variantClass, sizeClass]"
    v-bind="$attrs"
  >
    <slot />
  </component>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

export type Variant = 'default' | 'secondary' | 'ghost' | 'danger' | 'warning' | 'link'

export type Size = 'xs' | 'sm' | 'md' | 'lg'

type Props = {
  asLink?: boolean
  to?: string
  variant?: Variant
  size?: Size
  disabled?: boolean
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
  link: 'link-btn',
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
  padding: 0.35rem 0.65rem;
  font-size: 0.78rem !important;
}

.btn-md {
  padding: 0.48rem 0.8rem;
  font-size: 0.84rem !important;
}

.btn-lg {
  padding: 0.65rem 1rem;
  font-size: 0.95rem !important;
}

.btn {
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 0;
  gap: 0.35rem;
  font: inherit;
  font-weight: 600;
  border-radius: 8px;
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
  box-shadow: 0 0 0 2px var(--ring);
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
  background: transparent;
  color: var(--foreground);
  border-color: var(--border);
}

.ghost-btn:hover {
  background: var(--secondary);
}

.danger-btn {
  border: 1px solid;
  background: color-mix(in oklab, var(--destructive) 10%, transparent);
  color: var(--destructive);
  border-radius: 8px;
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

/* Text-only link. Drops the chrome so it reads as inline body text. */
.link-btn {
  padding: 0;
  border: 0;
  border-radius: 0;
  background: transparent;
  color: var(--primary);
  font-weight: inherit;
  text-decoration: underline;
  text-underline-offset: 0.15em;
  text-decoration-thickness: from-font;
}

.link-btn:hover {
  background: transparent;
  opacity: 0.75;
}

.link-btn:focus-visible {
  box-shadow: none;
  outline: 2px solid var(--ring);
  outline-offset: 2px;
}
</style>
