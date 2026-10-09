<template>
  <header class="tournaments-hero">
    <div class="tournaments-hero-copy">
      <div class="breadcrumb-label">
        <span>Workspace</span>
        <span aria-hidden="true">/</span>
        <span>Tournaments</span>
      </div>

      <h1 class="text-6xl">Tournaments list</h1>
      <p class="section-subtitle text-xl">
        Browse active competitions, track registration, and open tournament workspaces.
      </p>
    </div>

    <div class="hero-actions">
      <ui-skeleton-loader :loading="loading">
        <template #skeleton>
          <ui-skeleton variant="rect" width="148px" height="45px" />
        </template>

        <ui-card variant="stat" class="tournaments-stat-card">
          <strong class="text-xl">{{ total }}</strong>
          <span class="text-sm">Total results</span>
        </ui-card>
      </ui-skeleton-loader>

      <ui-button asLink to="/tournaments/archive" variant="default" size="lg">Archive</ui-button>
      <ui-button v-if="isAdmin" asLink to="/tournaments/create" size="lg">
        <span class="create-plus text-2xl" aria-hidden="true">+</span>
        Create tournament
      </ui-button>
    </div>
  </header>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'

defineProps<{
  total: number
  loading: boolean
  isAdmin: boolean
}>()
</script>

<style scoped>
.tournaments-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1.5rem;
}

.tournaments-hero-copy {
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

.tournaments-hero h1 {
  margin: 0;
  max-width: 760px;
  color: var(--foreground);
  font-size: var(--text-4xl);
  line-height: var(--text-4xl--line-height);
  font-family: var(--font-display);
  font-weight: 800;
}

.tournaments-hero .section-subtitle {
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

.tournaments-stat-card strong {
  font-weight: 800;
}

.tournaments-stat-card span {
  color: var(--muted-foreground);
  font-weight: 700;
  white-space: nowrap;
}

.create-plus {
  font-weight: 800;
  line-height: 1;
}

@media (max-width: 760px) {
  .tournaments-hero {
    align-items: stretch;
    flex-direction: column;
    gap: 1rem;
  }

  .tournaments-hero h1 {
    font-size: var(--text-3xl);
    line-height: var(--text-3xl--line-height);
  }

  .tournaments-hero .section-subtitle {
    font-size: var(--text-sm);
    line-height: var(--text-sm--line-height);
  }

  .hero-actions {
    justify-content: flex-start;
    align-items: flex-start;
  }
}
</style>
