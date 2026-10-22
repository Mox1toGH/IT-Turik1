<template>
  <header class="edit-hero">
    <div>
      <p class="section-eyebrow">Tournaments</p>
      <div class="heading-title-row">
        <h1>Edit tournament</h1>
        <ui-button
          asLink
          :to="`/tournaments/${tournamentId}`"
          variant="ghost"
          size="sm"
          class="back-button"
        >
          <ArrowLeft :size="16" aria-hidden="true" />
          Back to tournament
        </ui-button>
      </div>
      <p class="section-subtitle">
        Update the tournament details, team limits, and registration dates.
      </p>
    </div>
  </header>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton'
import { ArrowLeft } from 'lucide-vue-next'

defineProps<{
  tournamentId: number
}>()
</script>

<style scoped>
.edit-hero {
  display: block;
  margin-bottom: 0;
}

.heading-title-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.edit-hero h1 {
  margin: 0.35rem 0 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-size: var(--text-4xl);
  line-height: var(--text-4xl--line-height);
  font-weight: 800;
}

.edit-hero .section-subtitle {
  max-width: 680px;
  margin: 0.45rem 0 0;
}

.back-button {
  flex: 0 0 auto;
  width: max-content;
  max-width: 100%;
  white-space: nowrap;
}

@media (max-width: 760px) {
  .heading-title-row {
    align-items: flex-start;
  }

  .edit-hero h1 {
    font-size: var(--text-3xl);
    line-height: var(--text-3xl--line-height);
  }
}

@media (max-width: 560px) {
  .heading-title-row {
    flex-direction: column;
    gap: 0.6rem;
  }
}
</style>
