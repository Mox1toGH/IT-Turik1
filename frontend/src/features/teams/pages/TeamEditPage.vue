<template>
  <section class="page-shell teams-edit-page">
    <header class="edit-header">
      <router-link class="back-link" :to="team ? `/teams/${team.id}` : '/teams'">
        <arrow-left class="back-icon" aria-hidden="true" />
        Back to team
      </router-link>

      <div class="edit-header-copy">
        <ui-skeleton-loader :loading="isLoadingTeamInfo">
          <template #skeleton>
            <ui-skeleton variant="rect" height="34px" width="280px" />
          </template>

          <h1 :title="team?.name">Edit {{ truncateText(team?.name ?? 'team', 40) }}</h1>
        </ui-skeleton-loader>

        <p class="section-subtitle">Update the team profile and manage who belongs to it.</p>
      </div>
    </header>

    <template v-if="team">
      <div class="teams-rule" aria-hidden="true"></div>

      <ui-tabs :items="tabItems" query-key="tab" sticky>
        <template #profile>
          <team-edit-form :status="status" :loading="isLoadingTeamInfo" :team="team" />
        </template>

        <template #members>
          <team-manage-members :loading="isLoadingTeamInfo" :team="team" />
        </template>

        <template #invitations>
          <team-invitations :loading="isLoadingTeamInvitations" :invitations="invitationList" />
        </template>

        <template v-if="!team.is_in_active_tournament" #invite>
          <team-invite :team="team" />
        </template>
      </ui-tabs>
    </template>
  </section>
</template>

<script setup lang="ts">
import ArrowLeft from '@/icons/ArrowLeft.vue'
import { computed, watchEffect } from 'vue'
import TeamEditForm from '../components/team-edit/TeamEditForm.vue'
import { useRoute, useRouter } from 'vue-router'
import TeamManageMembers from '../components/team-edit/TeamManageMembers.vue'
import TeamInvite from '../components/team-edit/TeamInvite.vue'
import UiTabs, { type TabItem } from '@/components/ui/UiTabs'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader'
import UiSkeleton from '@/components/ui/UiSkeleton'
import { truncateText } from '@/lib/utils'
import { useGetUserProfile } from '@/api/accounts/accounts'
import { useCardState } from '@/composables/useCardState'
import { useGetTeam, useListTeamInvitationsByTeam } from '@/api/teams/teams'

const route = useRoute()
const router = useRouter()

const { data: user } = useGetUserProfile()

const teamId = computed(() => Number(route.params.id))
const teamQuery = useGetTeam(teamId.value)
const { data: team, isLoading: isLoadingTeamInfo } = teamQuery
const { status } = useCardState(teamQuery)

// Invitations query lives at page level (same cache key as any nested use, so
// no extra fetch): the pending count is needed here for the tab badge.
const { data: invitationsData, isLoading: isLoadingTeamInvitations } =
  useListTeamInvitationsByTeam(teamId)
const invitationList = computed(() => invitationsData.value ?? [])
const pendingInvitationCount = computed(
  () => invitationList.value.filter((invitation) => invitation.status === 'invited').length,
)

const tabItems = computed<TabItem[]>(() => {
  const items: TabItem[] = [
    { value: 'profile', label: 'Team profile' },
    { value: 'members', label: 'Members', count: team.value?.members.length },
    {
      value: 'invitations',
      label: 'Invitations',
      count: pendingInvitationCount.value > 0 ? pendingInvitationCount.value : undefined,
    },
  ]
  if (team.value && !team.value.is_in_active_tournament) {
    items.push({ value: 'invite', label: 'Invite' })
  }
  return items
})

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
  gap: 1.4rem;
}

.edit-header {
  display: grid;
  gap: 0.6rem;
  min-width: 0;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  width: max-content;
  color: var(--muted-foreground);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  font-weight: 700;
  text-decoration: none;
}

.back-link:hover {
  color: var(--foreground);
  text-decoration: underline;
  text-underline-offset: 2px;
}

.back-link:focus-visible {
  outline: 2px solid var(--ring);
  outline-offset: 2px;
  border-radius: 4px;
}

.back-icon {
  width: 1rem;
  height: 1rem;
  flex: 0 0 auto;
}

.edit-header h1 {
  margin: 0;
  max-width: 760px;
  overflow: hidden;
  color: var(--foreground);
  font-family: var(--font-display);
  font-size: var(--text-3xl);
  line-height: var(--text-3xl--line-height);
  font-weight: 800;
  text-overflow: ellipsis;
}

.section-subtitle {
  max-width: 680px;
  margin: 0.35rem 0 0;
}

.teams-rule {
  height: 1px;
  margin: 0.7rem 0 0.9rem;
  background: var(--border);
}

@media (max-width: 720px) {
  .teams-edit-page {
    padding: 1rem 1rem 2rem;
  }

  .edit-header h1 {
    font-size: var(--text-2xl);
    line-height: var(--text-2xl--line-height);
  }
}
</style>
