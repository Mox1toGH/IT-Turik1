<template>
  <ui-card class="create-hero">
    <div>
      <p class="section-eyebrow">Tournament workspace</p>
      <h1>Create tournament</h1>
      <p class="section-subtitle">
        Set the public details, team limits, and registration window before rounds are added.
      </p>
    </div>

    <ui-button asLink to="/tournaments" variant="secondary" size="lg" class="back-link">
      Back to tournaments
    </ui-button>
  </ui-card>
  <CreateTournamentForm />
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import CreateTournamentForm from '../components/tournament-create/CreateTournamentForm.vue'
</script>

<style scoped>
.create-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1.5rem;
  margin-bottom: 1rem;
}

.create-hero h1 {
  margin: 0.35rem 0 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-size: var(--text-4xl);
  line-height: var(--text-4xl--line-height);
  font-weight: 800;
}

.create-hero .section-subtitle {
  max-width: 680px;
  margin: 0.45rem 0 0;
}

.back-link {
  flex: 0 0 auto;
}

@media (max-width: 760px) {
  .create-hero {
    flex-direction: column;
    align-items: flex-start;
    padding: 1.2rem;
  }

  .create-hero h1 {
    font-size: var(--text-3xl);
    line-height: var(--text-3xl--line-height);
  }
}
</style>
