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
          variant="secondary"
          :disabled="props.status !== 'draft'"
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
            size="sm"
            :disabled="props.status !== 'active'"
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
            :disabled="props.status !== 'submission_closed'"
            class="action-btn"
            @click="
              () => {
                close()
                handleMarkEvaluated()
              }
            "
          >
            Mark evaluated
          </ui-button>
          <ui-button
            size="sm"
            class="action-btn action-delete"
            variant="danger"
            :disabled="props.status !== 'draft'"
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
import type { StatusE43Enum } from '@/api/.ts.schemas'
import { useGetUserProfile } from '@/api/accounts/accounts'
import {
  useCloseRoundSubmissions,
  useDeleteRound,
  useMarkRoundEvaluated,
  useStartRound,
} from '@/api/tournaments/tournaments'
import UiButton from '@/components/ui/UiButton.vue'
import UiPopover from '@/components/ui/UiPopover.vue'
import { useNotification } from '@/composables/useNotification'
import ThreeCenterDotsIcon from '@/icons/ThreeCenterDotsIcon.vue'

interface Props {
  roundId: number
  tournamentId: number
  status: StatusE43Enum
}

const props = defineProps<Props>()
const { showNotification } = useNotification()

const { data: profile } = useGetUserProfile()
const { mutate: deleteRound } = useDeleteRound()
const { mutate: startRound } = useStartRound()
const { mutate: closeSubmissions } = useCloseRoundSubmissions()
const { mutate: markEvaluated } = useMarkRoundEvaluated()

function handleDeleteRound() {
  deleteRound(
    {
      id: props.roundId,
    },
    {
      onError: (error) => {
        showNotification(error?.message, 'error')
      },
    },
  )
}

function handleStartRound() {
  startRound(
    {
      id: props.roundId,
    },
    {
      onError: (error) => {
        showNotification(error?.message, 'error')
      },
    },
  )
}

function handleCloseSubmissions() {
  closeSubmissions(
    {
      id: props.roundId,
    },
    {
      onError: (error) => {
        showNotification(error?.message, 'error')
      },
    },
  )
}

function handleMarkEvaluated() {
  markEvaluated(
    {
      id: props.roundId,
    },
    {
      onError: (error) => {
        showNotification(error?.message, 'error')
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
  color: var(--foreground);
}

.action-btn:hover {
  background: color-mix(in srgb, var(--secondary) 60%, transparent);
}

.action-delete {
  border: 0;
  background: color-mix(in srgb, var(--destructive) 10%, transparent);
  color: var(--destructive);
}

.action-delete:hover {
  background: color-mix(in srgb, var(--destructive) 15%, transparent);
}
</style>
