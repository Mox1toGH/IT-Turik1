<template>
  <section class="page-shell tournament-create-page">
    <page-back-link to="/tournaments" label="Back to tournaments" />
    <header class="page-heading">
      <div>
        <p class="section-eyebrow">Tournaments</p>
        <h1>Create tournament</h1>
        <p class="section-subtitle">
          Set the tournament details, team limits, and registration dates.
        </p>
      </div>
    </header>

    <tournament-form mode="create" />
  </section>
</template>

<script setup lang="ts">
import PageBackLink from '@/components/shared/PageBackLink.vue'
import TournamentForm from '../components/tournament-form/TournamentForm.vue'
</script>

<style scoped>
.tournament-create-page {
  gap: 1.4rem;
}

.page-heading {
  display: block;
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

@media (max-width: 760px) {
  .tournament-create-page {
    padding: 1rem 1rem 2rem;
  }

  .page-heading h1 {
    font-size: var(--text-3xl);
    line-height: var(--text-3xl--line-height);
  }
}

</style>
