<template>
  <ui-popover minWidth="180px" header="actions">
    <template #trigger="{ toggle }">
      <ui-button variant="secondary" class="actions-trigger" size="sm" @click="toggle"
        ><three-center-dots-icon width="18"
      /></ui-button>
    </template>

    <template #default="{ close }">
      <div class="actions-list">
        <ui-button
          v-if="props.status === 'draft'"
          variant="secondary"
          size="sm"
          class="action-btn"
          @click="
            () => {
              close()
              handleStartRound()
            }
          "
          >Start round</ui-button
        >
        <template v-if="profile?.role === 'admin'">
          <ui-button
            v-if="props.status === 'active'"
            size="sm"
            class="action-btn"
            @click="
              () => {
                close()
                handleCloseSubmissions()
              }
            "
          >
            Close submissions
          </ui-button>
          <ui-button
            size="sm"
            class="action-btn action-delete"
            variant="danger"
            @click="
              () => {
                close()
                handleDeleteRound()
              }
            "
          >
            Delete
          </ui-button>
        </template>
      </div>
    </template>
  </ui-popover>
</template>

<script setup lang="ts">
import type { RoundId, RoundStatus, TournamentId } from '@/api/dbTypes'
import { parseApiError } from '@/api/errors'
import { useProfile } from '@/api/queries/accounts'
import { useCloseSubmissions, useDeleteRound, useStartRound } from '@/api/queries/tournaments'
import UiButton from '@/components/ui/UiButton.vue'
import UiPopover from '@/components/ui/UiPopover.vue'
import { useNotification } from '@/composables/useNotification'
import ThreeCenterDotsIcon from '@/icons/ThreeCenterDotsIcon.vue'

interface Props {
  roundId: RoundId
  tournamentId: TournamentId
  status: RoundStatus
}

const props = defineProps<Props>()
const { showNotification } = useNotification()

const { data: profile } = useProfile()
const { mutate: deleteRound } = useDeleteRound({ id: props.tournamentId })
const { mutate: startRound } = useStartRound()
const { mutate: closeSubmissions } = useCloseSubmissions()

function handleDeleteRound() {
  deleteRound(
    {
      id: props.roundId,
    },
    {
      onError: (error) => {
        const parsedError = parseApiError(error)
        showNotification(parsedError?.message, 'error')
      },
    },
  )
}

function handleStartRound() {
  startRound(
    {
      roundId: props.roundId,
    },
    {
      onError: (error) => {
        const parsedError = parseApiError(error)
        showNotification(parsedError?.message, 'error')
      },
    },
  )
}

function handleCloseSubmissions() {
  closeSubmissions(
    {
      roundId: props.roundId,
    },
    {
      onError: (error) => {
        const parsedError = parseApiError(error)
        showNotification(parsedError?.message, 'error')
      },
    },
  )
}
</script>

<style scoped>
.actions-trigger {
  padding: 0.2rem 0.5rem;
}

.actions-list {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.action-btn {
  text-align: start;
  justify-content: start;
  background: transparent;
}

.action-btn:hover {
  background: color-mix(in srgb, var(--secondary) 60%, transparent);
}

.action-delete {
  border: 0;
  background: color-mix(in srgb, var(--destructive) 10%, transparent);
}

.action-delete:hover {
  background: color-mix(in srgb, var(--destructive) 15%, transparent);
}
</style>
