<template>
  <section class="edit-tournament-page page-shell">
    <edit-tournament-hero :tournament-id="tournamentId" />
    <tournament-form :tournament-id="tournamentId" />
  </section>
</template>

<script setup lang="ts">
import EditTournamentHero from '../components/tournament-edit/EditTournamentHero.vue'
import TournamentForm from '../components/tournament-edit/TournamentForm.vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const tournamentId = Number(route.params.id)
</script>

<style scoped>
.edit-tournament-page {
  gap: 1.4rem;
  padding: 1.6rem 0 2rem;
}

@media (max-width: 760px) {
  .edit-tournament-page {
    padding: 1rem 1rem 2rem;
  }
}
</style>
