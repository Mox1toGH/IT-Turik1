<template>
  <ui-card :is-error="props.loadingError">
    <template #error>
      <div style="display: flex; justify-content: center; align-items: center; height: 502px">
        <p>Failed to fetch team info</p>
      </div>
    </template>

    <template #header>
      <div class="panel-head">
        <h2>Team Info</h2>
        <ui-skeleton-loader :loading="props.loading">
          <template #skeleton>
            <ui-skeleton variant="rect" width="150px" />
          </template>
        </ui-skeleton-loader>
      </div>
    </template>

    <div>
      <div class="info-grid">
        <ui-card title="Name" class="info-item">
          <template #header>
            <span class="card-label">Name</span>
          </template>

          <ui-skeleton-loader :loading="props.loading">
            <template #skeleton>
              <ui-skeleton variant="rect" width="100%" style="margin-top: 5px" />
            </template>

            <strong class="text-muted" :title="props.team?.name">{{
              truncateText(props.team?.name ?? '', 35)
            }}</strong>
          </ui-skeleton-loader>
        </ui-card>

        <ui-card title="Email" class="info-item">
          <template #header>
            <span class="card-label">Email</span>
          </template>

          <ui-skeleton-loader :loading="props.loading">
            <template #skeleton>
              <ui-skeleton variant="rect" width="100%" style="margin-top: 5px" />
            </template>

            <strong class="text-muted">{{ props.team?.email }}</strong>
          </ui-skeleton-loader>
        </ui-card>

        <ui-card title="Organization" class="info-item">
          <template #header>
            <span class="card-label">Organization</span>
          </template>

          <ui-skeleton-loader :loading="props.loading">
            <template #skeleton>
              <ui-skeleton variant="rect" width="100%" style="margin-top: 5px" />
            </template>

            <strong class="text-muted">{{ props.team?.organization || '-' }}</strong>
          </ui-skeleton-loader>
        </ui-card>

        <ui-card title="Captain" class="info-item">
          <template #header>
            <span class="card-label">Captain</span>
          </template>

          <ui-skeleton-loader :loading="props.loading">
            <template #skeleton>
              <ui-skeleton variant="rect" width="100%" style="margin-top: 5px" />
            </template>

            <strong v-if="props.team?.captain_id">
              <RouterLink :to="`/users/${props.team.captain_id}`" class="captain-link">
                {{ captainName }}
              </RouterLink>
            </strong>
            <strong v-else class="text-muted">{{ captainName }}</strong>
          </ui-skeleton-loader>
        </ui-card>

        <ui-card title="Members count" class="info-item">
          <template #header>
            <span class="card-label">Members count</span>
          </template>

          <ui-skeleton-loader :loading="props.loading">
            <template #skeleton>
              <ui-skeleton variant="rect" width="100%" style="margin-top: 5px" />
            </template>

            <strong class="text-muted">{{ props.team?.members.length }}</strong>
          </ui-skeleton-loader>
        </ui-card>

        <ui-card title="Visibility" class="info-item">
          <template #header>
            <span class="card-label">Visibility</span>
          </template>

          <ui-skeleton-loader :loading="props.loading">
            <template #skeleton>
              <ui-skeleton variant="rect" width="100%" style="margin-top: 5px" />
            </template>

            <strong class="text-muted">{{ props.team?.is_public ? 'Public' : 'Private' }}</strong>
          </ui-skeleton-loader>
        </ui-card>
      </div>
    </div>

    <template #footer>
      <div class="info-actions">
        <ui-button
          v-if="props.team?.can_request_to_join"
          size="sm"
          :disabled="joinRequestLoading"
          @click="sendJoinRequest"
        >
          <loading-icon v-if="joinRequestLoading" size="md" />
          {{ joinRequestLoading ? 'Sending...' : 'Request to join this team' }}
        </ui-button>

        <ui-button v-if="canLeaveTeam" variant="danger" size="sm" @click="leaveTeam">
          Leave team
        </ui-button>
      </div>
    </template>
  </ui-card>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import { computed } from 'vue'
import { useNotification } from '@/composables/useNotification'
import { useLeaveTeam, useSendJoinRequest } from '@/api/queries/teams'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import type { GetTeamInfoResponse } from '@/api/services/teams/types'
import { truncateText } from '@/lib/utils'

interface Props {
  team?: GetTeamInfoResponse
  loading: boolean
  loadingError?: boolean
  isCaptain: boolean
}

const props = defineProps<Props>()
const { showNotification, hideNotification } = useNotification()

const emit = defineEmits<{
  (e: 'deleted'): void
  (e: 'leave'): void
}>()

const captainName = computed(() => {
  const captain = props.team?.members.find((member) => member.id === props.team?.captain_id)
  return captain?.username || `User #${props.team?.captain_id}`
})

const canLeaveTeam = computed(() => props.team?.is_member && !props.isCaptain)

// ── Join Request ────────────────────────────────────────────────────
const { mutate: sendJoinRequestMutate, isPending: joinRequestLoading } = useSendJoinRequest()

const sendJoinRequest = () => {
  if (!props.team) return
  hideNotification()

  sendJoinRequestMutate(
    { id: props.team?.id },
    {
      onSuccess: () => {
        emit('deleted')
        showNotification('Join request sent.', 'success')
      },
      onError: (err) => {
        showNotification(
          err.response ? 'Unable to send join request.' : 'Server connection error.',
          'error',
        )
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
    { id: props.team.id },
    {
      onSuccess: () => {
        emit('leave')
      },
      onError: (err) => {
        showNotification(
          err.response ? 'Unable to leave team.' : 'Unable to connect to server.',
          'error',
        )
      },
    },
  )
}
</script>

<style scoped>
.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.7rem;
}

.info-grid {
  display: grid;
  gap: 0.65rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  border: 1px solid var(--line-soft);
  border-radius: 12px;
  gap: 0.3rem;
  background: var(--muted);
}

.info-item span {
  display: block;
  font-size: 0.8rem;
}

.captain-link {
  color: var(--brand-700);
  text-decoration: none;
  font-weight: 700;
}

.info-actions {
  display: flex;
  gap: 0.55rem;
  flex-wrap: wrap;
}

.modal-text {
  margin: 0 0 0.75rem;
  font-size: 0.9rem;
  color: var(--color-gray-700);
  line-height: 1.55;
}

.modal-text code {
  background: #f1f5f9;
  border: 1px solid var(--line-soft);
  border-radius: 6px;
  padding: 0.1rem 0.35rem;
  font-family: 'SF Mono', ui-monospace, monospace;
  font-size: 0.85em;
}

.modal-error {
  margin: 0.5rem 0 0;
  font-size: 0.8rem;
}

@media (max-width: 1020px) {
  .hero-top {
    flex-direction: column;
  }

  .hero-contacts {
    justify-items: start;
  }

  .workspace-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .member-row,
  .manage-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .member-side {
    align-items: flex-start;
  }

  .status-tags {
    justify-content: flex-start;
  }
}
</style>
