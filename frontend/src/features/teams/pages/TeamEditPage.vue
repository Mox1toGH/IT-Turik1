<template>
  <section class="page-shell teams-edit-page">
    <header class="edit-header">
      <page-back-link :to="team ? `/teams/${team.id}` : '/teams'" label="Back to team" />

      <div class="edit-header-copy">
        <h1 :title="team?.name">
          <ui-query-field :loading="isLoadingTeamInfo">
            <template #skeleton>
              <ui-skeleton variant="rect" height="34px" width="280px" />
            </template>
            Edit {{ truncateText(team?.name ?? 'team', 40) }}
          </ui-query-field>
        </h1>

        <p class="section-subtitle">Update the team profile and manage who belongs to it.</p>
      </div>
    </header>

    <template v-if="team">
      <div class="teams-rule" aria-hidden="true"></div>

      <ui-tabs :items="tabItems" query-key="tab" sticky>
        <template #profile>
          <team-edit-form :loading="isLoadingTeamInfo" :team="team" />
        </template>

        <template #members>
          <team-manage-members
            :loading="isLoadingMembers"
            :team="team"
            :members="members"
            :query="membersQuery"
          />
        </template>

        <template #invitations>
          <team-invitations :invitations="invitationList" :query="invitationsQuery" />
        </template>

        <template v-if="!team.is_in_active_tournament" #invite>
          <team-invite :team="team" />
        </template>
      </ui-tabs>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, watchEffect } from 'vue'
import PageBackLink from '@/components/shared/PageBackLink.vue'
import TeamEditForm from '../components/team-edit/TeamEditForm.vue'
import { useRoute, useRouter } from 'vue-router'
import TeamManageMembers from '../components/team-edit/TeamManageMembers.vue'
import TeamInvitations from '../components/team-edit/TeamInvitations.vue'
import TeamInvite from '../components/team-edit/TeamInvite.vue'
import UiTabs, { type TabItem } from '@/components/ui/UiTabs'
import { UiQueryField } from '@/components/query'
import UiSkeleton from '@/components/ui/UiSkeleton'
import { truncateText } from '@/lib/utils'
import { useGetUserProfile } from '@/api/accounts/accounts'
import {
  useGetTeam,
  useListTeamInvitationsByTeam,
  useListTeamMembers,
} from '@/api/teams/teams'
import { isTeamCaptain } from '../lib/team-permissions'
import type { TeamMember } from '../types'

const route = useRoute()
const router = useRouter()

const { data: user } = useGetUserProfile()

const teamId = computed(() => Number(route.params.id))
const teamQuery = useGetTeam(teamId.value)
const { data: team, isLoading: isLoadingTeamInfo } = teamQuery
const membersQuery = useListTeamMembers(teamId, {
  query: { enabled: computed(() => route.query.tab === 'members') },
})
const { data: memberResponses, isLoading: isLoadingMembers } = membersQuery
const members = computed<TeamMember[]>(() =>
  (memberResponses.value ?? []).map((member) => ({
    id: member.id,
    username: member.username,
    email: member.email,
    full_name: member.full_name,
    role: member.role,
    avatar: member.avatar,
  })),
)

// Invitations query lives at page level (same cache key as any nested use, so
// no extra fetch): the pending count is needed here for the tab badge.
const invitationsQuery = useListTeamInvitationsByTeam(teamId)
const { data: invitationsData } = invitationsQuery
const invitationList = computed(() => invitationsData.value?.items ?? [])
const pendingInvitationCount = computed(
  () => invitationList.value.filter((invitation) => invitation.status === 'invited').length,
)

const tabItems = computed<TabItem[]>(() => {
  const items: TabItem[] = [
    { value: 'profile', label: 'Team profile' },
    {
      value: 'members',
      label: 'Members',
      count: memberResponses.value ? members.value.length : team.value?.members.length,
    },
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
    if (!isTeamCaptain(user.value, team.value)) {
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
