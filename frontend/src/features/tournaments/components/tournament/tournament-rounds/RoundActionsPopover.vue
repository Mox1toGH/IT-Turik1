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
                showDeleteModal = true
              }
            "
          >
            Delete
          </ui-button>
        </template>
      </div>
    </template>
  </ui-popover>

  <ui-confirm-modal
    v-model="showDeleteModal"
    title="Delete round?"
    message="This action cannot be undone. The round and all its data will be permanently removed."
    confirm-text="Delete"
    confirm-variant="danger"
    @confirm="handleDeleteRound"
  />
</template>

<script setup lang="ts">
import type { RoundId, RoundStatus, TournamentId } from '@/api/dbTypes'
import { parseApiError } from '@/api/errors'
import { useProfile } from '@/api/queries/accounts'
import {
  useCloseSubmissions,
  useDeleteRound,
  useMarkEvaluated,
  useStartRound,
} from '@/api/queries/tournaments'
import UiButton from '@/components/ui/UiButton.vue'
import UiConfirmModal from '@/components/ui/UiConfirmModal.vue'
import UiPopover from '@/components/ui/UiPopover.vue'
import { useNotification } from '@/composables/useNotification'
import ThreeCenterDotsIcon from '@/icons/ThreeCenterDotsIcon.vue'
import { ref } from 'vue'

interface Props {
  roundId: RoundId
  tournamentId: TournamentId
  status: RoundStatus
}

const props = defineProps<Props>()
const { showNotification } = useNotification()

const showDeleteModal = ref(false)

const { data: profile } = useProfile()
const { mutate: deleteRound } = useDeleteRound({ id: props.tournamentId })
const { mutate: startRound } = useStartRound()
const { mutate: closeSubmissions } = useCloseSubmissions()
const { mutate: markEvaluated } = useMarkEvaluated()

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

function handleMarkEvaluated() {
  markEvaluated(
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
