<template>
  <ui-card class="edit-hero">
    <div>
      <p class="section-eyebrow">Tournament workspace</p>
      <h1>Edit tournament</h1>
      <p class="section-subtitle">
        Update the public details, team limits, and registration window for this tournament.
      </p>
    </div>

    <ui-button
      asLink
      :to="`/tournaments/${tournamentId}`"
      variant="secondary"
      size="lg"
      class="back-link"
    >
      Back to tournament
    </ui-button>
  </ui-card>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'

defineProps<{
  tournamentId: number
}>()
</script>

<style scoped>
.edit-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1.5rem;
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

.back-link {
  flex: 0 0 auto;
}

@media (max-width: 760px) {
  .edit-hero {
    flex-direction: column;
    align-items: flex-start;
    padding: 1.2rem;
  }

  .edit-hero h1 {
    font-size: var(--text-3xl);
    line-height: var(--text-3xl--line-height);
  }
}
</style>
