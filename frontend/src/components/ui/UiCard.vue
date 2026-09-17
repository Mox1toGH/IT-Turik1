<template>
  <div :class="['card', variantClass, { scrollable: props.scrollable }]">
    <slot v-if="$slots.header" name="header" />

    <Transition name="error-fade" role="alert">
      <div v-if="props.isError">
        <slot name="error" />
      </div>
    </Transition>

    <slot v-if="!props.isError && $slots.default" />

    <slot v-if="$slots.footer" name="footer" />
  </div>
</template>

<script setup lang="ts">
interface Props {
  isError?: boolean
  scrollable?: boolean
  variant?: 'default' | 'panel' | 'stat' | 'hero' | 'form' | 'actions' | 'inset'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
})

const variantClass = `card-${props.variant}`
</script>

<style scoped>
.card {
  border: 1px solid;
  border-color: inherit;
  border-radius: 14px;
  padding: 1.2rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  background: var(--card);
  color: var(--card-foreground);
  box-shadow: 0 5px 20px 0 rgb(0 0 0 / 0.05);
}

.card-panel {
  gap: 1.7rem;
  padding: 2.4rem 2rem 1.8rem;
  border-color: var(--line-soft);
  border-radius: 20px;
  background: var(--card);
}

.card-stat {
  min-width: 148px;
  min-height: 64px;
  padding: 0.9rem 1.1rem;
  align-items: center;
  justify-content: center;
  flex-direction: row;
  gap: 0.7rem;
  border-color: var(--line-soft);
  border-radius: 14px;
  background: var(--card);
}

.card-hero {
  padding: 1.5rem;
  border-color: var(--line-soft);
  border-radius: 20px;
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--primary) 10%, transparent), transparent 44%),
    var(--card);
}

.card-form {
  gap: 1rem;
  padding: 1.25rem;
  border-color: var(--line-soft);
  border-radius: 18px;
  background: var(--card);
}

.card-actions {
  padding: 0.8rem;
  border-color: var(--line-soft);
  border-radius: 16px;
  background: color-mix(in srgb, var(--card) 92%, transparent);
  backdrop-filter: blur(12px);
}

.card-inset {
  padding: 0.8rem;
  border-color: var(--line-soft);
  border-radius: 12px;
  background: color-mix(in srgb, var(--card) 92%, var(--foreground) 8%);
}

.card.scrollable {
  max-height: calc(100vh - 16px * 2);
  overflow-y: auto;
}

@media (max-width: 700px) {
  .card-panel {
    padding: 1.4rem;
  }
}

.error-fade-enter-active,
.error-fade-leave-active {
  transition: opacity 0.15s ease;
}

.error-fade-enter-from,
.error-fade-leave-to {
  opacity: 0;
}
</style>
