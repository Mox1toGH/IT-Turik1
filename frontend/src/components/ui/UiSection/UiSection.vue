<template>
  <section class="ui-section" :class="{ 'ui-section--divider': divider }">
    <div v-if="title || $slots.actions" class="ui-section__head">
      <div class="ui-section__titles">
        <h2 v-if="title" class="ui-section__title">{{ title }}</h2>
        <p v-if="description" class="ui-section__description">{{ description }}</p>
      </div>
      <div v-if="$slots.actions" class="ui-section__actions">
        <slot name="actions" />
      </div>
    </div>
    <slot />
  </section>
</template>

<script setup lang="ts">
interface Props {
  title?: string
  description?: string
  divider?: boolean
}

withDefaults(defineProps<Props>(), {
  title: undefined,
  description: undefined,
  divider: false,
})
</script>

<style scoped>
.ui-section {
  min-width: 0;
}

.ui-section--divider {
  border-top: 1px solid var(--border);
  padding-top: 2rem;
}

.ui-section__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
  min-width: 0;
}

.ui-section__titles {
  min-width: 0;
}

.ui-section__title {
  margin: 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-size: var(--text-xl);
  line-height: var(--text-xl--line-height);
  font-weight: 800;
  overflow-wrap: anywhere;
}

.ui-section__description {
  margin: 0.25rem 0 0;
  color: var(--muted-foreground);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  overflow-wrap: anywhere;
}

.ui-section__actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 0 0 auto;
}
</style>
