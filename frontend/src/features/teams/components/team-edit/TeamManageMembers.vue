<template>
  <div class="members-panel">
    <ui-input
      v-model="memberSearch"
      class="search-input"
      placeholder="Search by username or email"
      :disabled="props.loading"
    />

    <ui-query-block :query="props.query">
      <ui-query-field>
        <template #skeleton>
          <div class="member-grid">
            <div v-for="i in 4" :key="`member-skeleton-${i}`" class="member-card-skeleton">
              <div class="member-card-skeleton-top">
                <ui-skeleton variant="rounded" width="44px" height="44px" />
                <div class="member-card-skeleton-lines">
                  <ui-skeleton variant="rect" width="120px" height="14px" />
                  <ui-skeleton variant="rect" width="160px" height="12px" />
                </div>
              </div>
            </div>
          </div>
        </template>
        <div class="member-grid">
          <ui-card
            v-for="member in filteredMembers"
            :key="`member-${member.id}`"
            class="member-card card-actions-divided"
          >
            <div class="member-top">
              <user-avatar
                :avatar="member.avatar"
                :username="member.username"
                :full-name="member.full_name || ''"
                :size="44"
              />

              <div class="member-main">
                <p class="member-name">
                  <RouterLink :to="`/users/${member.id}`" class="member-link">
                    {{ member.username }}
                  </RouterLink>
                </p>
                <p class="text-muted member-email">{{ member.email }}</p>
              </div>

              <ui-badge v-if="member.id === team?.captain_id" variant="green">Captain</ui-badge>
              <ui-badge v-else variant="gray">Member</ui-badge>
            </div>

            <template v-if="canRemove(member)" #footer>
              <ui-button
                variant="danger"
                size="sm"
                class="remove-member-btn"
                :disabled="kickLoadingIds.has(member.id)"
                @click="requestRemoveMember(member)"
              >
                <LoaderCircle class="animate-spin" v-if="kickLoadingIds.has(member.id)" />
                Remove
              </ui-button>
            </template>
          </ui-card>
        </div>
        <p v-if="filteredMembers?.length === 0" class="text-muted members-note">
          No members match your search.
        </p>
      </ui-query-field>
    </ui-query-block>
    <ui-confirm-modal
      v-model="isRemoveConfirmOpen"
      title="Remove team member?"
      :message="pendingRemoval
        ? `Remove ${pendingRemoval.username} from ${team.name}? They will lose access to the team.`
        : 'Remove this person from the team?'"
      confirm-text="Remove member"
      confirm-variant="danger"
      :loading="isRemovingPendingMember"
      @confirm="confirmRemoveMember"
    />
  </div>
</template>

<script setup lang="ts">
import UiBadge from '@/components/ui/UiBadge'
import UiButton from '@/components/ui/UiButton'
import UiCard from '@/components/ui/UiCard'
import UiInput from '@/components/ui/UiInput'
import UiConfirmModal from '@/components/ui/UiConfirmModal'
import { UiQueryBlock, UiQueryField } from '@/components/query'
import UiSkeleton from '@/components/ui/UiSkeleton'
import UserAvatar from '@/components/shared/UserAvatar.vue'
import { useNotification } from '@/composables/useNotification'
import { LoaderCircle } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'
import {
  getListTeamMembersQueryKey,
  useRemoveMemberFromTeam,
} from '@/api/teams/teams'
import type { TeamMember } from '@/features/teams/types'
import type { Team } from '@/features/teams/types'
import type { QueryLike } from '@/composables/useQueryState'
import { useQueryClient } from '@tanstack/vue-query'

interface Props {
  team: Team
  members: TeamMember[]
  loading: boolean
  query: QueryLike
}

const props = defineProps<Props>()
const { showNotification } = useNotification()
const queryClient = useQueryClient()

const memberSearch = ref('')
const kickLoadingIds = ref<Set<number>>(new Set())
const pendingRemoval = ref<TeamMember | null>(null)
const isRemoveConfirmOpen = ref(false)
const isRemovingPendingMember = computed(
  () => pendingRemoval.value !== null && kickLoadingIds.value.has(pendingRemoval.value.id),
)

const filteredMembers = computed(() => {
  const search = memberSearch.value.trim().toLowerCase()
  if (!search) return props.members
  return props.members.filter((member) =>
    [member.username, member.email, member.full_name || '']
      .join(' ')
      .toLowerCase()
      .includes(search),
  )
})

const canRemove = (member: TeamMember) =>
  member.id !== props.team.captain_id && !props.team.is_in_active_tournament

const { mutate: removeMemberMutate } = useRemoveMemberFromTeam()

const removeMember = (member: TeamMember) => {
  if (!props.team) return
  if (member.id === props.team.captain_id) return
  kickLoadingIds.value.add(member.id)

  removeMemberMutate(
    { pk: props.team.id, userId: member.id },
    {
      onSuccess: () => {
        isRemoveConfirmOpen.value = false
        pendingRemoval.value = null
        void queryClient.invalidateQueries({
          queryKey: getListTeamMembersQueryKey(props.team.id),
        })
        showNotification('Member removed.', 'success')
      },
      onError: (error) => {
        showNotification(error.message, 'error')
      },
      onSettled: () => {
        kickLoadingIds.value.delete(member.id)
      },
    },
  )
}

const requestRemoveMember = (member: TeamMember) => {
  pendingRemoval.value = member
  isRemoveConfirmOpen.value = true
}

const confirmRemoveMember = () => {
  if (pendingRemoval.value) removeMember(pendingRemoval.value)
}
</script>

<style scoped>
.members-panel {
  display: grid;
  gap: 1.25rem;
  min-width: 0;
}

.search-input {
  width: 100%;
}

.member-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.25rem;
}

.member-card {
  height: 100%;
  min-width: 0;
  gap: 1rem;
}

.member-top {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 0;
}

.member-main {
  flex: 1;
  min-width: 0;
}

.member-name {
  margin: 0;
  font-weight: 700;
  min-width: 0;
  overflow-wrap: anywhere;
}

.member-link {
  color: var(--primary);
  text-decoration: none;
  font-weight: 700;
}

.member-link:hover {
  text-decoration: underline;
  text-underline-offset: 2px;
}

.member-email {
  margin: 0.15rem 0 0;
  font-size: 0.84rem;
  overflow-wrap: anywhere;
}

.remove-member-btn {
  width: max-content;
}

.members-note {
  margin: 0;
  padding: 1rem 0;
  text-align: center;
}

.member-card-skeleton {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  height: 100%;
  padding: 1.2rem;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--card);
}

.member-card-skeleton-top {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.member-card-skeleton-lines {
  display: grid;
  gap: 0.4rem;
}
</style>
