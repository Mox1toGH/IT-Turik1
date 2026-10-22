<template>
  <section class="page-shell tournament-create-page">
    <header class="page-heading">
      <div>
        <p class="section-eyebrow">Tournaments</p>
        <div class="heading-title-row">
          <h1>Create tournament</h1>
          <ui-button asLink to="/tournaments" variant="ghost" size="sm" class="back-button">
            <ArrowLeft :size="16" aria-hidden="true" />
            Back to tournaments
          </ui-button>
        </div>
        <p class="section-subtitle">
          Set the tournament details, team limits, and registration dates.
        </p>
      </div>
    </header>

    <CreateTournamentForm />
  </section>
</template>

<script setup lang="ts">
import { ArrowLeft } from 'lucide-vue-next'
import UiButton from '@/components/ui/UiButton'
import CreateTournamentForm from '../components/tournament-create/CreateTournamentForm.vue'
</script>

<style scoped>
.tournament-create-page {
  gap: 1.4rem;
}

.page-heading {
  display: block;
}

.heading-title-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.page-heading h1 {
  margin: 0.35rem 0 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-size: var(--text-4xl);
  line-height: var(--text-4xl--line-height);
  font-weight: 800;
}

.page-heading .section-subtitle {
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
  .tournament-create-page {
    padding: 1rem 1rem 2rem;
  }

  .heading-title-row {
    align-items: flex-start;
  }

  .page-heading h1 {
    font-size: var(--text-3xl);
    line-height: var(--text-3xl--line-height);
  }
}

@media (max-width: 560px) {
  .heading-title-row {
    align-items: flex-start;
    flex-direction: column;
    gap: 0.6rem;
  }
}
</style>
