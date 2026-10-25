<template>
  <section :class="['card', `card-${variant}`, { scrollable }]">
    <header v-if="$slots.header || title" class="card-header">
      <slot name="header">
        <h3 class="card-title">{{ title }}</h3>
        <p v-if="subtitle" class="card-subtitle">{{ subtitle }}</p>
      </slot>
    </header>

    <div class="card-body">
      <slot />
    </div>

    <footer v-if="$slots.footer" class="card-footer">
      <slot name="footer" />
    </footer>
  </section>
</template>

<script setup lang="ts">
interface Props {
  title?: string
  subtitle?: string
  scrollable?: boolean
  variant?: 'default' | 'panel' | 'stat' | 'hero' | 'form' | 'inset'
}

withDefaults(defineProps<Props>(), {
  variant: 'default',
})
</script>

<style scoped>
.card {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1.2rem;
  border: 1px solid var(--border);
  border-radius: 14px;
  background: var(--card);
  color: var(--card-foreground);
  box-shadow: 0 5px 20px rgb(0 0 0 / 0.05);
}
.dark .card {
  box-shadow: 0 5px 20px rgb(0 0 0 / 0.25);
}

.card-panel {
  gap: 1.7rem;
  padding: 2.4rem 2rem 1.8rem;
  border-color: var(--line-soft);
  border-radius: 20px;
}
.card-stat {
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 0.7rem;
  min-width: 100px;
  padding: 0.5rem 1.1rem;
  border-color: var(--line-soft);
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
}
.card-inset {
  padding: 0.8rem;
  border-color: var(--line-soft);
  border-radius: 12px;
  background: color-mix(in srgb, var(--card) 92%, var(--foreground) 8%);
}

.card-title {
  margin: 0;
  font-size: 1rem;
}
.card-subtitle {
  margin: 0.15rem 0 0;
  font-size: 0.85rem;
  color: var(--muted-foreground);
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.card.scrollable {
  max-height: calc(100vh - 32px);
}
.card.scrollable > .card-body {
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
}

@media (max-width: 700px) {
  .card-panel {
    padding: 1.4rem;
  }
}
</style>
