<template>
  <section class="page-shell teams-edit-page">
    <ui-card>
      <template #header>
        <div>
          <p class="section-eyebrow">Team workspace</p>

          <h1 class="section-title">
            Edit
            <ui-skeleton-loader style="display: inline-block" :loading="isLoadingTeamInfo">
              <template #skeleton>
                <ui-skeleton variant="rect" width="150px" />
              </template>

              <span :title="team?.name">{{ truncateText(team?.name ?? 'team', 45) }}</span>
            </ui-skeleton-loader>
          </h1>
        </div>
      </template>

      <template #footer>
        <ui-button
          asLink
          variant="secondary"
          size="sm"
          class="back-btn"
          :to="team ? `/teams/${team.id}` : '/teams'"
          >Back to team</ui-button
        >
      </template>
    </ui-card>

    <div class="workspace-grid" v-if="team">
      <team-edit-form :is-error="isError" :loading="isLoadingTeamInfo" :team="team" />

      <team-manage-members :is-error="isError" :loading="isLoadingTeamInfo" :team="team" />
    </div>
  </section>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import { computed, watchEffect } from 'vue'
import TeamEditForm from '../components/team-edit/TeamEditForm.vue'
import { useRoute, useRouter } from 'vue-router'
import TeamManageMembers from '../components/team-edit/TeamManageMembers.vue'
import { useTeamInfo } from '@/api/queries/teams'
import { useProfile } from '@/api/queries/accounts'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import { truncateText } from '@/lib/utils'

const route = useRoute()
const router = useRouter()

const { data: user } = useProfile()

const teamId = computed(() => Number(route.params.id))
const { data: team, isLoading: isLoadingTeamInfo, isError } = useTeamInfo({ id: teamId.value })

watchEffect(() => {
  if (user.value && team.value) {
    if (team.value.captain_id !== user.value.id) {
      router.push('/')
    }
  }
})
</script>

<style scoped>
.teams-edit-page {
  gap: 1.2rem;
}

.back-btn {
  width: max-content;
}

.workspace-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  align-items: start;
}
</style>
