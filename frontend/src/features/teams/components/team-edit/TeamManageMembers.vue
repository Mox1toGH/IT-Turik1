<template>
  <ui-card class="panel members-panel" :is-error="props.isError">
    <template #error>
      <div style="display: flex; justify-content: center; align-items: center; height: 302px">
        <p>Failed to fetch team members</p>
      </div>
    </template>

    <template #header>
      <header class="panel-head">
        <h2>Members management</h2>
        <ui-skeleton-loader :loading="props.loading">
          <template #skeleton>
            <ui-skeleton variant="rect" width="100px" />
          </template>

          <span class="text-muted">{{ team?.members.length ?? 0 }} people</span>
        </ui-skeleton-loader>
      </header>
    </template>

    <div class="form-item">
      <ui-input
        class="search-input"
        v-model="memberSearch"
        placeholder="Search by username or email"
        :disabled="props.loading"
      />
    </div>

    <ui-skeleton-loader :loading="props.loading">
      <template #skeleton>
        <div class="member-list">
          <ui-card v-for="i in 2" :key="i" class="member-row">
            <template #header>
              <div style="display: flex; justify-content: space-between; gap: 10px">
                <ui-skeleton variant="rect" width="140px" />
                <ui-skeleton variant="rect" width="120px" />
              </div>
            </template>

            <ui-skeleton variant="rect" width="100px" />

            <template #footer>
              <ui-skeleton variant="rect" height="30px" width="70px" />
            </template>
          </ui-card>
        </div>
      </template>

      <div class="member-list">
        <ui-card v-for="member in filteredMembers" :key="`member-${member.id}`" class="member-row">
          <div>
            <div style="display: flex; justify-content: space-between; gap: 10px">
              <p class="member-name">
                <RouterLink :to="`/users/${member.id}`" class="member-link">
                  {{ member.username }}
                </RouterLink>
              </p>
              <div style="display: flex; align-items: center; gap: 5px">
                <ui-badge v-if="member.id === team?.captain_id" variant="green">Captain</ui-badge>
              </div>
            </div>

            <p class="text-muted member-email">{{ member.email }}</p>
          </div>

          <template #footer>
            <ui-button
              v-if="member.id !== team?.captain_id && !team.is_in_active_tournament"
              variant="danger"
              size="sm"
              class="remove-member-btn"
              :disabled="kickLoadingIds.has(member.id)"
              @click="removeMember(member)"
            >
              <loading-icon v-if="kickLoadingIds.has(member.id)" />
              Remove
            </ui-button>
          </template>
        </ui-card>
      </div>
    </ui-skeleton-loader>

    <div class="add-member-box">
      <h3>Invitations status</h3>

      <ui-skeleton-loader :loading="props.loading">
        <template #skeleton>
          <div class="member-list">
            <ui-card v-for="i in 2" :key="i" class="member-row">
              <div style="display: flex; justify-content: space-between; gap: 10px">
                <ui-skeleton variant="rect" width="80px" />
                <ui-skeleton variant="rect" width="100px" />
              </div>
            </ui-card>
          </div>
        </template>

        <div class="member-list">
          <p v-if="!isLoadingInvitations && !invitations?.length" class="text-muted">
            No invitations yet.
          </p>
          <ui-card
            v-for="invitation in invitations"
            :key="`inv-${invitation.id}`"
            class="member-row"
          >
            <div style="display: flex; justify-content: space-between; gap: 10px">
              <p class="member-name">{{ invitation.user.username }}</p>

              <ui-badge v-if="invitation.status === 'declined'" variant="red">
                {{ invitation.status }}
              </ui-badge>
              <ui-badge v-if="invitation.status === 'accepted'" variant="green">{{
                invitation.status
              }}</ui-badge>
              <ui-badge v-else>{{ invitation.status }}</ui-badge>
            </div>
          </ui-card>
        </div>
      </ui-skeleton-loader>
    </div>

    <p v-if="filteredMembers?.length === 0" class="text-muted member-note">
      No members match your search.
    </p>

    <div class="add-member-box" v-if="!team.is_in_active_tournament">
      <h3>Invite user</h3>

      <ui-select
        placeholder="Select user"
        v-model="addMemberSelection"
        :options="userOptions"
        :isLoading="isLoadingUsers"
      />

      <ui-button
        @click="addMember"
        :disabled="addMemberLoading || isLoadingUsers || !addMemberSelection"
      >
        {{ addMemberLoading ? 'Sending...' : 'Send invitation' }}
      </ui-button>
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import UiBadge from '@/components/ui/UiBadge.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiSelect from '@/components/ui/UiSelect.vue'
import { useNotification } from '@/composables/useNotification'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import { computed, ref } from 'vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import type { Team, TeamMember } from '@/api/.ts.schemas'
import {
  useInviteMemberToTeam,
  useListTeamInvitationsByTeam,
  useRemoveMemberFromTeam,
} from '@/api/teams/teams'
import { useListUsers } from '@/api/accounts/accounts'

interface Props {
  team: Team
  loading: boolean
  isError?: boolean
}

const props = defineProps<Props>()
const { showNotification } = useNotification()

const { data: users, isLoading: isLoadingUsers } = useListUsers()
const { data: invitations, isLoading: isLoadingInvitations } = useListTeamInvitationsByTeam(
  props.team.id,
)

const memberSearch = ref('')
const addMemberSelection = ref<number | null>(null)
const kickLoadingIds = ref<Set<number>>(new Set())

const availableUsers = computed(() => {
  const currentIds = new Set(props.team?.members.map((member) => member.id))
  return users.value?.filter((user) => !currentIds.has(user.id))
})

const filteredMembers = computed(() => {
  const search = memberSearch.value.trim().toLowerCase()
  if (!search) return props.team?.members
  return props.team?.members.filter((member) =>
    [member.username, member.email, member.full_name || '']
      .join(' ')
      .toLowerCase()
      .includes(search),
  )
})

const userOptions = computed(() => [
  ...(availableUsers.value?.map((user) => ({
    value: String(user.id),
    label: `${user.username} (${user.email})`,
  })) || []),
])

// ── Remove member ─────────────────────────────────────────────
const { mutate: removeMemberMutate } = useRemoveMemberFromTeam()

const removeMember = (member: TeamMember) => {
  if (!props.team) return
  if (member.id === props.team.captain_id) return
  kickLoadingIds.value.add(member.id)

  removeMemberMutate(
    { id: props.team.id, userId: member.id },
    {
      onSuccess: () => {
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

// ── Add member ────────────────────────────────────────────────
const { mutate: addMemberMutate, isPending: addMemberLoading } = useInviteMemberToTeam()

const addMember = () => {
  if (!props.team) return

  if (!addMemberSelection.value) {
    showNotification('Select a user to add.', 'error')
    return
  }

  addMemberMutate(
    { id: props.team.id, data: { user_id: Number(addMemberSelection.value) } },
    {
      onSuccess: () => {
        addMemberSelection.value = null
        showNotification('Invitation sent.', 'success')
      },
      onError: (error) => {
        showNotification(error.message, 'error')
      },
    },
  )
}
</script>

<style scoped>
.panel {
  border: 1px solid var(--line-soft);
}

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.7rem;
  margin-bottom: 0.9rem;
}

.search-input {
  margin-bottom: 12px;
}

.panel-head h2 {
  margin: 0;
  font-family: var(--font-display);
  font-size: 1.15rem;
}

.member-row {
  background-color: var(--muted);
  color: var(--muted-foreground);
}

.member-list {
  display: grid;
  gap: 0.55rem;
}

.member-name,
.member-email {
  margin: 0;
}

.member-name {
  font-weight: 700;
}

.member-link {
  color: var(--brand-700);
  text-decoration: none;
  font-weight: 700;
}

.member-email {
  font-size: 0.84rem;
}
.member-note {
  margin-top: 0.8rem;
}

.remove-member-btn {
  width: max-content;
}

.add-member-box {
  margin-top: 0.9rem;
  border-top: 1px solid var(--line-soft);
  padding-top: 0.9rem;
  display: grid;
  gap: 0.65rem;
}

.add-member-box h3 {
  margin: 0;
  font-size: 1rem;
}
</style>
