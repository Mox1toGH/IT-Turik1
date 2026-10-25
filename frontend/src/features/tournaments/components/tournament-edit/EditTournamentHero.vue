<template>
  <header class="edit-hero">
    <page-back-link :to="`/tournaments/${tournamentId}`" label="Back to tournament" />
    <div>
      <p class="section-eyebrow">Tournaments</p>
      <h1>Edit tournament</h1>
      <p class="section-subtitle">
        Update the tournament details, team limits, and registration dates.
      </p>
    </div>
  </header>
</template>

<script setup lang="ts">
import PageBackLink from '@/components/shared/PageBackLink.vue'

defineProps<{
  tournamentId: number
}>()
</script>

<style scoped>
.edit-hero {
  display: grid;
  gap: 0.8rem;
  margin-bottom: 0;
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

@media (max-width: 760px) {
  .edit-hero h1 {
    font-size: var(--text-3xl);
    line-height: var(--text-3xl--line-height);
  }
}

</style>
