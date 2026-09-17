<template>
  <ui-card class="panel members-panel" variant="form" :is-error="props.isError">
    <template #error>
      <div class="empty-state">
        <p>Failed to fetch team members</p>
      </div>
    </template>

    <template #header>
      <div class="panel-header">
        <span class="step-marker">02</span>
        <div>
          <h2>Members</h2>
          <p class="text-muted">Review current members and manage pending invitations.</p>
        </div>
        <ui-skeleton-loader :loading="props.loading">
          <template #skeleton>
            <ui-skeleton variant="rect" width="100px" />
          </template>

          <ui-card variant="stat" class="members-stat">
            <strong>{{ team?.members.length ?? 0 }}</strong>
            <span>People</span>
          </ui-card>
        </ui-skeleton-loader>
      </div>
    </template>

    <div class="teams-rule" aria-hidden="true"></div>

    <div class="form-item search-field">
      <p class="form-label">Search members</p>
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
              <div class="member-row-top">
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
        <ui-card
          v-for="member in filteredMembers"
          :key="`member-${member.id}`"
          class="member-row"
          variant="inset"
        >
          <div>
            <div class="member-row-top">
              <p class="member-name">
                <RouterLink :to="`/users/${member.id}`" class="member-link">
                  {{ member.username }}
                </RouterLink>
              </p>
              <div class="member-badges">
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
      <div class="box-header">
        <h3>Invitations status</h3>
        <span class="text-muted">{{ invitations?.length ?? 0 }} pending total</span>
      </div>

      <ui-skeleton-loader :loading="props.loading">
        <template #skeleton>
          <div class="member-list">
            <ui-card v-for="i in 2" :key="i" class="member-row">
              <div class="member-row-top">
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
            variant="inset"
          >
            <div class="member-row-top">
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
      <div class="box-header">
        <h3>Invite user</h3>
        <span class="text-muted">Add a new teammate by invitation.</span>
      </div>

      <div class="form-item">
        <p class="form-label">User</p>
        <ui-select
          placeholder="Select user"
          v-model="addMemberSelection"
          :options="userOptions"
          :isLoading="isLoadingUsers"
        />
      </div>

      <ui-button
        size="lg"
        class="invite-btn"
        @click="addMember"
        :disabled="addMemberLoading || isLoadingUsers || !addMemberSelection"
      >
        <loading-icon v-if="addMemberLoading" />
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
.teams-rule {
  height: 1px;
  margin: 0.7rem 0 0.9rem;
  background: var(--line-soft);
}

.members-stat {
  margin-left: auto;
}

.members-stat strong {
  color: var(--foreground);
  font-family: var(--font-display);
  font-size: var(--text-xl);
  line-height: var(--text-xl--line-height);
  font-weight: 800;
}

.members-stat span {
  color: var(--muted-foreground);
  font-size: var(--text-xs);
  line-height: var(--text-xs--line-height);
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.search-field {
  margin-top: 0.25rem;
}

.member-list {
  display: grid;
  gap: 0.65rem;
}

.member-row.card {
  gap: 0.65rem;
  color: var(--muted-foreground);
}

.member-row-top,
.box-header {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
}

.member-row-top {
  align-items: flex-start;
}

.box-header {
  align-items: baseline;
}

.box-header span {
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  text-align: right;
}

.member-badges {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  flex-wrap: wrap;
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
  display: grid;
  gap: 0.75rem;
  margin-top: 0.35rem;
  padding: 1rem;
  border: 1px solid var(--line-soft);
  border-radius: 14px;
}

.add-member-box h3 {
  margin: 0;
  font-size: 1rem;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 302px;
}

@media (max-width: 760px) {
  .panel-header,
  .member-row-top,
  .box-header {
    flex-direction: column;
  }

  .box-header span {
    text-align: left;
  }

  .remove-member-btn {
    width: 100%;
  }
}
</style>
