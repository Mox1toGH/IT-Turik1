<template>
  <HoverCardRoot :open-delay="150" :close-delay="100" :enable-touch="true">
    <HoverCardTrigger as-child>
      <slot name="trigger" />
    </HoverCardTrigger>

    <HoverCardPortal>
      <HoverCardContent class="hover-card-content" :side="side" :align="align" :side-offset="6">
        <slot />
        <HoverCardArrow class="hover-card-arrow" />
      </HoverCardContent>
    </HoverCardPortal>
  </HoverCardRoot>
</template>

<script setup lang="ts">
import {
  HoverCardArrow,
  HoverCardContent,
  HoverCardPortal,
  HoverCardRoot,
  HoverCardTrigger,
} from 'reka-ui'

withDefaults(
  defineProps<{
    side?: 'top' | 'right' | 'bottom' | 'left'
    align?: 'start' | 'center' | 'end'
  }>(),
  {
    side: 'top',
    align: 'center',
  },
)
</script>

<style scoped>
:deep(.hover-card-content) {
  z-index: 10000;
  max-width: min(280px, calc(100vw - 2rem));
  padding: 0.65rem 0.8rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--popover, var(--background));
  color: var(--popover-foreground, var(--foreground));
  box-shadow: var(--shadow-overlay);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
}

:deep(.hover-card-arrow) {
  fill: var(--popover, var(--background));
}
</style>
