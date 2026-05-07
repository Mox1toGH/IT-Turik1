<template>
  <section class="page-shell">
    <ui-card>
      <template #header>
        <div>
          <div class="top-header">
            <p class="section-eyebrow">Teams</p>

            <ui-skeleton-loader :loading="isLoadingTeams">
              <template #skeleton>
                <ui-skeleton variant="rect" width="108px" height="30px" />
              </template>

              <ui-badge>Total teams: {{ teams?.length ?? '0' }}</ui-badge>
            </ui-skeleton-loader>
          </div>
          <h1>Team directory</h1>
          <p class="section-subtitle">
            Open a team workspace to view details, edit info, and manage members.
          </p>
        </div>
      </template>

      <template #footer>
        <div class="hero-actions">
          <ui-button asLink to="/teams/create" class="manage-link">Create new team</ui-button>
        </div>
      </template>
    </ui-card>

    <team-invatations />

    <team-my-teams />

    <teams-other-teams />
  </section>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import TeamInvatations from '../components/teams-list/TeamInvatations.vue'
import TeamMyTeams from '../components/teams-list/TeamMyTeams.vue'
import TeamsOtherTeams from '../components/teams-list/TeamsOtherTeams.vue'
import { useTeams } from '@/api/queries/teams'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiBadge from '@/components/ui/UiBadge.vue'

const { data: teams, isLoading: isLoadingTeams } = useTeams()
</script>

<style scoped>
.top-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.hero-actions {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
  align-items: center;
}

.manage-link {
  display: inline-flex;
}
</style>
