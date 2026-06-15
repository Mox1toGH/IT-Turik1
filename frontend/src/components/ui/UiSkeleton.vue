<template>
  <div
    aria-busy="true"
    aria-live="polite"
    aria-label="loading"
    :class="['skeleton', 'animated', variantClass]"
    :style="styleVars"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'

export type Variant = 'rect' | 'rounded'

interface Props {
  variant?: Variant
  width?: string | number
  height?: string | number
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'rect',
  width: '100%',
  height: '24px',
})

const styleVars = computed(() => {
  const width = typeof props.width === 'number' ? `${props.width}px` : props.width
  const height = typeof props.height === 'number' ? `${props.height}px` : props.height

  return { width, height }
})

const variantClass = computed(() => `skeleton--${props.variant}`)
</script>

<style scoped>
.skeleton {
  background: linear-gradient(
    90deg,
    color-mix(in srgb, var(--foreground) 10%, transparent) 0%,
    color-mix(in srgb, var(--foreground) 16%, transparent) 50%,
    color-mix(in srgb, var(--foreground) 10%, transparent) 100%
  );
  background-size: 200% 100%;
  border-radius: 4px;
}

.skeleton.animated {
  animation: shimmer 2s infinite linear;
}

.skeleton--rounded {
  border-radius: 50%;
}

.skeleton--rect {
  border-radius: 8px;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>
