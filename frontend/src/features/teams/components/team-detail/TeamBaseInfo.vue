<template>
  <ui-card :status="props.status" :error-code="props.errorCode">
    <template #error>
      <div style="display: flex; justify-content: center; align-items: center; height: 502px">
        <p>Failed to fetch team info</p>
      </div>
    </template>

    <template #header>
      <div class="panel-header">
        <span class="step-marker">01</span>
        <div>
          <h2>Team info</h2>
          <p class="text-muted">Core identity, ownership, and directory status.</p>
        </div>
      </div>
    </template>

    <div>
      <div class="info-grid">
        <div class="info-row">
          <span class="card-label">Name</span>
          <ui-skeleton-loader :loading="props.loading">
            <template #skeleton>
              <ui-skeleton variant="rect" width="100%" style="margin-top: 5px" />
            </template>

            <strong class="text-muted info-value">
              <ui-truncate :text="props.team?.name ?? ''" />
            </strong>
          </ui-skeleton-loader>
        </div>

        <div class="info-row">
          <span class="card-label">Email</span>
          <ui-skeleton-loader :loading="props.loading">
            <template #skeleton>
              <ui-skeleton variant="rect" width="100%" style="margin-top: 5px" />
            </template>

            <strong class="text-muted info-value">{{ props.team?.email }}</strong>
          </ui-skeleton-loader>
        </div>

        <div class="info-row">
          <span class="card-label">Organization</span>
          <ui-skeleton-loader :loading="props.loading">
            <template #skeleton>
              <ui-skeleton variant="rect" width="100%" style="margin-top: 5px" />
            </template>

            <strong class="text-muted info-value">{{ props.team?.organization || '-' }}</strong>
          </ui-skeleton-loader>
        </div>

        <div class="info-row">
          <span class="card-label">Captain</span>
          <ui-skeleton-loader :loading="props.loading">
            <template #skeleton>
              <ui-skeleton variant="rect" width="100%" style="margin-top: 5px" />
            </template>

            <strong v-if="props.team?.captain_id" class="info-value">
              <RouterLink :to="`/users/${props.team.captain_id}`" class="captain-link">
                {{ captainName }}
              </RouterLink>
            </strong>
            <strong v-else class="text-muted info-value">{{ captainName }}</strong>
          </ui-skeleton-loader>
        </div>

        <div class="info-row">
          <span class="card-label">Members count</span>
          <ui-skeleton-loader :loading="props.loading">
            <template #skeleton>
              <ui-skeleton variant="rect" width="100%" style="margin-top: 5px" />
            </template>

            <strong class="text-muted info-value">{{ props.team?.members.length }}</strong>
          </ui-skeleton-loader>
        </div>

        <div class="info-row">
          <span class="card-label">Visibility</span>
          <ui-skeleton-loader :loading="props.loading">
            <template #skeleton>
              <ui-skeleton variant="rect" width="100%" style="margin-top: 5px" />
            </template>

            <strong class="text-muted info-value">{{
              props.team?.is_public ? 'Public' : 'Private'
            }}</strong>
          </ui-skeleton-loader>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="info-actions">
        <ui-button
          v-if="props.team?.can_request_to_join && user?.role === 'team'"
          size="md"
          :disabled="joinRequestLoading"
          @click="sendJoinRequest"
        >
          <loading-icon v-if="joinRequestLoading" size="md" />
          {{ joinRequestLoading ? 'Sending...' : 'Request to join this team' }}
        </ui-button>

        <ui-button
          v-if="canLeaveTeam"
          class="leave-team"
          variant="danger"
          size="md"
          @click="leaveTeam"
        >
          Leave team
        </ui-button>
      </div>
    </template>
  </ui-card>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton'
import UiCard from '@/components/ui/UiCard'
import UiTruncate from '@/components/ui/UiTruncate'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import { computed } from 'vue'
import { useNotification } from '@/composables/useNotification'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader'
import UiSkeleton from '@/components/ui/UiSkeleton'
import type { CardErrorCode, CardStatus } from '@/composables/useCardState'
import { useCreateTeamJoinRequest, useLeaveTeam } from '@/api/teams/teams'
import { useGetUserProfile } from '@/api/accounts/accounts'
import type { TeamResponse } from '@/api/backendAPINinja.schemas'

interface Props {
  team?: TeamResponse
  loading: boolean
  status: CardStatus
  errorCode: CardErrorCode
  isCaptain: boolean
}

const props = defineProps<Props>()
const { showNotification, hideNotification } = useNotification()

const emit = defineEmits<{
  (e: 'deleted'): void
  (e: 'leave'): void
}>()

const { data: user } = useGetUserProfile()

const captainName = computed(() => {
  const captain = props.team?.members.find((member) => member.id === props.team?.captain_id)
  return captain?.username || `User #${props.team?.captain_id}`
})

const canLeaveTeam = computed(() => props.team?.is_member && !props.isCaptain)

// ── Join Request ────────────────────────────────────────────────────
const { mutate: sendJoinRequestMutate, isPending: joinRequestLoading } = useCreateTeamJoinRequest()

const sendJoinRequest = () => {
  if (!props.team) return
  hideNotification()

  sendJoinRequestMutate(
    { pk: props.team?.id },
    {
      onSuccess: () => {
        emit('deleted')
        showNotification('Join request sent.', 'success')
      },
      onError: (error) => {
        showNotification(error.message, 'error')
      },
    },
  )
}

// ── Leave Team ────────────────────────────────────────────────────
const { mutate: leaveTeamMutate } = useLeaveTeam()

const leaveTeam = () => {
  if (!props.team) return
  hideNotification()

  leaveTeamMutate(
    { pk: props.team.id },
    {
      onSuccess: () => {
        emit('leave')
      },
      onError: (error) => {
        showNotification(error.message, 'error')
      },
    },
  )
}
</script>

<style scoped>
.panel-header {
  display: flex;
  align-items: flex-start;
  gap: 0.85rem;
}

.panel-header h2 {
  margin: 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-size: var(--text-xl);
  line-height: var(--text-xl--line-height);
  font-weight: 800;
}

.panel-header p {
  margin: 0;
}

.step-marker {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
  min-width: 2.15rem;
  height: 2.15rem;
  padding: 0 0.55rem;
  border-radius: 999px;
  background: var(--primary-soft);
  color: var(--primary);
  font-size: var(--text-xs);
  line-height: var(--text-xs--line-height);
  font-weight: 900;
  text-transform: uppercase;
}

.info-grid {
  display: grid;
  gap: 0;
  border-top: 1px solid var(--border);
}

.info-row {
  display: grid;
  grid-template-columns: minmax(0, 0.8fr) minmax(0, 1fr);
  gap: 0.75rem;
  padding: 0.8rem 0;
}

.info-row + .info-row {
  border-top: 1px solid var(--border);
}

.info-value {
  min-width: 0;
  overflow-wrap: anywhere;
}

.captain-link {
  color: var(--primary);
  text-decoration: none;
  font-weight: 700;
}

.captain-link:hover {
  text-decoration: underline;
  text-underline-offset: 2px;
}

.info-actions {
  display: flex;
  gap: 0.55rem;
  flex-wrap: wrap;
}

.info-actions .leave-team {
  width: 100%;
}
</style>
