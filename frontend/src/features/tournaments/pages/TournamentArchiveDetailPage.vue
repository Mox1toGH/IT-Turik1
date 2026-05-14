<template>
  <section class="page-shell">
    <ui-card>
      <template #header>
        <div class="header">
          <h1>{{ archive?.name ?? `Archive ${id}` }}</h1>
          <div class="actions">
            <ui-button asLink to="/tournaments/archive" size="sm" variant="secondary">Back</ui-button>
            <ui-button asLink :to="`/tournaments/${id}`" size="sm" variant="secondary">Open tournament</ui-button>
          </div>
        </div>
      </template>

      <ui-skeleton-loader :loading="isLoading">
        <template #skeleton>
          <ui-skeleton variant="rect" height="220px" />
        </template>

        <template v-if="archive">
          <p>{{ archive.description }}</p>

          <h3>Final Standings</h3>
          <div v-if="archive.standings.length" class="table">
            <div class="table-row table-head">
              <span>Rank</span>
              <span>Team</span>
              <span>Total</span>
              <span>Average</span>
            </div>
            <div v-for="row in archive.standings" :key="`${row.rank}-${row.team.id}`" class="table-row">
              <span>{{ row.rank }}</span>
              <span>{{ row.team.name }}</span>
              <span>{{ row.total_score }}</span>
              <span>{{ row.average_score }}</span>
            </div>
          </div>
          <p v-else>No saved standings.</p>

          <h3>Participating Teams</h3>
          <ul class="teams">
            <li v-for="team in archive.teams" :key="team.id">{{ team.name }}</li>
          </ul>

          <details>
            <summary>Submissions and evaluations ({{ submissions.length }})</summary>
            <div class="subs">
              <ui-card v-for="submission in submissions" :key="submission.id" class="sub-item">
                <p><strong>Team:</strong> {{ submission.team_details.name }}</p>
                <p><strong>Round:</strong> {{ submission.round_details.name }}</p>
                <p><strong>GitHub:</strong> {{ submission.github_url }}</p>
                <p><strong>Evaluations:</strong> {{ submission.assignments.length }}</p>
              </ui-card>
            </div>
          </details>
        </template>
      </ui-skeleton-loader>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import { useRoute } from 'vue-router'
import { computed } from 'vue'
import { useTournamentArchiveDetail, useTournamentArchiveSubmissions } from '@/api/queries/tournaments'

const route = useRoute()
const id = Number(route.params.id)
const { data, isLoading } = useTournamentArchiveDetail({ id })
const { data: submissionsData } = useTournamentArchiveSubmissions({ id })
const archive = computed(() => data.value)
const submissions = computed(() => submissionsData.value ?? [])
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.actions {
  display: flex;
  gap: 8px;
}

.table {
  border: 1px solid var(--line-soft);
  border-radius: 8px;
  overflow: hidden;
}

.table-row {
  display: grid;
  grid-template-columns: 80px 1fr 120px 120px;
  gap: 8px;
  padding: 8px 12px;
  border-top: 1px solid var(--line-soft);
}

.table-head {
  border-top: 0;
  font-weight: 600;
  background: var(--muted);
}

.teams {
  padding-left: 18px;
}

.subs {
  display: grid;
  gap: 8px;
  margin-top: 8px;
}

.sub-item {
  background: var(--muted) !important;
}

@media (max-width: 720px) {
  .table-row {
    grid-template-columns: 60px 1fr 90px 90px;
    font-size: 13px;
  }
}
</style>
