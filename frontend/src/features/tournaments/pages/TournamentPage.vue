<template>
  <section class="tournament-detail-page page-shell">
    <TournamentHeroCard :tournament-id="id" />

    <div class="tournament-rule" aria-hidden="true"></div>

    <ui-tabs :items="tabItems" query-key="section">
      <template #information>
        <div class="tournament-grid">
          <TournamentInfo :tournament-id="id" />
          <TournamentTeams :tournament-id="id" />
        </div>

        <ManageZoneCard
          v-if="user?.role === 'admin'"
          :tournament-id="id"
          class="manage-zone"
        />
      </template>

      <template #rounds>
        <TournamentRounds :tournament-id="id" />
      </template>

      <template #submissions>
        <template v-if="user">
          <TournamentSubmissions v-if="user?.role === 'team'" :tournament-id="id" />
          <JuryAssign
            v-else-if="user?.role === 'admin'"
            :tournament-id="id"
            :tournament-status="tournament?.status ?? 'draft'"
          />
          <ui-card v-else>
            <p>Submissions are available for team members and admins.</p>
          </ui-card>
        </template>
        <ui-card v-else-if="userQuery.isError.value">
          <p>Could not load your access level.</p>
        </ui-card>
      </template>

      <template #schedule>
        <TournamentSchedule
          :tournament-id="id"
          :tournament-status="tournament?.status ?? 'draft'"
        />
      </template>

      <template #leaderboard>
        <TournamentLeaderboard :tournament-id="id" />
      </template>
    </ui-tabs>
  </section>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard'
import UiTabs, { type TabItem } from '@/components/ui/UiTabs'
import { useRoute } from 'vue-router'
import TournamentInfo from '../components/tournament/tabs/TournamentInfo.vue'
import TournamentTeams from '../components/tournament/tabs/TournamentTeams.vue'
import { computed } from 'vue'
import TournamentSchedule from '../components/tournament/tabs/TournamentSchedule.vue'
import TournamentRounds from '../components/tournament/tabs/TournamentRounds.vue'
import JuryAssign from '../components/tournament/tabs/tournament-submissions/JuryAssign.vue'
import TournamentSubmissions from '../components/tournament/tabs/TournamentSubmissions.vue'
import TournamentLeaderboard from '../components/tournament/tabs/TournamentLeaderboard.vue'

import { useGetUserProfile } from '@/api/accounts/accounts'
import { useGetTournament } from '@/api/tournaments/tournaments'
import ManageZoneCard from '../components/tournament/ManageZoneCard.vue'
import TournamentHeroCard from '../components/tournament/TournamentHeroCard.vue'

const route = useRoute()

const id = Number(route.params.id)

const userQuery = useGetUserProfile()
const { data: user } = userQuery
const tournamentQuery = useGetTournament(id)
const { data: tournament } = tournamentQuery

const canViewSubmissions = computed(() => user.value?.role === 'admin' || user.value?.role === 'team')

const tabItems = computed<TabItem[]>(() => [
  { value: 'information', label: 'Information' },
  { value: 'rounds', label: 'Rounds' },
  { value: 'submissions', label: 'Submissions', disabled: !canViewSubmissions.value },
  { value: 'schedule', label: 'Schedule' },
  { value: 'leaderboard', label: 'Leaderboard' },
])
</script>

<style scoped>
.tournament-detail-page {
  gap: 1.4rem;
}

.tournament-rule {
  height: 1px;
  margin: 0.7rem 0 0.9rem;
  background: var(--border);
}

.tournament-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(280px, 0.7fr);
  gap: 1rem;
  align-items: start;
}

.manage-zone {
  margin-top: 1rem;
}

@media (max-width: 810px) {
  .tournament-detail-page {
    padding: 1rem 1rem 2rem;
  }

  .tournament-grid {
    grid-template-columns: 1fr;
  }
}
</style>
