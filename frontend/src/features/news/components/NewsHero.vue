<template>
  <header class="news-hero">
    <div class="news-hero-copy">
      <div class="breadcrumb-label">
        <span>Workspace</span>
        <span aria-hidden="true">/</span>
        <span>News</span>
      </div>

      <h1 class="text-6xl">News board</h1>
      <p class="section-subtitle text-xl">
        Important updates, announcements, and platform changes.
      </p>
    </div>

    <div class="hero-actions">
      <ui-card variant="stat" class="news-stat-card">
        <strong class="text-xl">{{ totalNews }}</strong>
        <span class="text-sm">Total posts</span>
      </ui-card>

      <ui-button v-if="canManageNews" size="lg" @click="$emit('create')">
        <span class="create-plus text-2xl" aria-hidden="true">+</span>
        Create news
      </ui-button>
    </div>
  </header>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard.vue'
import UiButton from '@/components/ui/UiButton.vue'

defineProps<{
  totalNews: number
  canManageNews: boolean
}>()

defineEmits<{
  create: []
}>()
</script>

<style scoped>
.news-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1.5rem;
}

.news-hero-copy {
  min-width: 0;
}

.breadcrumb-label {
  display: inline-flex;
  align-items: center;
  gap: 0.7rem;
  margin-bottom: 0.75rem;
  color: var(--accent-strong);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.news-hero h1 {
  margin: 0;
  max-width: 760px;
  color: var(--foreground);
  font-size: var(--text-4xl);
  line-height: var(--text-4xl--line-height);
  font-family: var(--font-display);
  font-weight: 800;
}

.news-hero .section-subtitle {
  margin: 0.45rem 0 0;
  max-width: 780px;
  font-size: var(--text-base);
  line-height: var(--text-base--line-height);
}

.hero-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: flex-end;
  align-items: center;
}

.news-stat-card {
  display: flex;
}

.news-stat-card strong {
  font-weight: 800;
}

.news-stat-card span {
  color: var(--muted-foreground);
  font-weight: 700;
  white-space: nowrap;
}

.create-plus {
  font-weight: 800;
  line-height: 1;
}

@media (max-width: 760px) {
  .news-hero {
    align-items: stretch;
    flex-direction: column;
    gap: 1rem;
  }

  .news-hero h1 {
    font-size: var(--text-3xl);
    line-height: var(--text-3xl--line-height);
  }

  .news-hero .section-subtitle {
    font-size: var(--text-sm);
    line-height: var(--text-sm--line-height);
  }

  .hero-actions {
    justify-content: flex-start;
  }
}
</style>
