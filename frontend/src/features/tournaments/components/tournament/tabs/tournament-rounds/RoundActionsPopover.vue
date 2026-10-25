<template>
  <ui-popover minWidth="180px" header="actions">
    <template #trigger>
      <ui-button variant="secondary" class="actions-trigger" size="sm"
        ><MoreHorizontal :size="18"
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
              requestConfirmation('start')
            }
          "
          >Start round</ui-button
        >
        <template v-if="hasRole(profile, 'admin')">
          <ui-button
            size="sm"
            :disabled="props.status !== 'active'"
            class="action-btn"
            @click="
              () => {
                close()
                requestConfirmation('close')
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
                requestConfirmation('evaluate')
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
                requestConfirmation('delete')
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
    v-model="isConfirmOpen"
    :title="confirmation.title"
    :message="confirmation.message"
    :confirm-text="confirmation.confirmText"
    :confirm-variant="pendingAction === 'delete' ? 'danger' : 'default'"
    :loading="isPending"
    @confirm="performConfirmedAction"
  />
</template>

<script setup lang="ts">
import { useGetUserProfile } from '@/api/accounts/accounts'
import { hasRole } from '@/shared/lib/permissions'
import type { RoundStatus } from '@/features/tournaments/types'
import {
  useCloseRoundSubmissions,
  useDeleteRound,
  useMarkRoundEvaluated,
  useStartRound,
} from '@/api/tournaments/tournaments'
import UiButton from '@/components/ui/UiButton'
import UiPopover from '@/components/ui/UiPopover'
import UiConfirmModal from '@/components/ui/UiConfirmModal'
import { useNotification } from '@/composables/useNotification'
import { MoreHorizontal } from 'lucide-vue-next'
import { computed, ref } from 'vue'

interface Props {
  roundId: number
  tournamentId: number
  status: RoundStatus
}

const props = defineProps<Props>()
const { showNotification } = useNotification()

const profileQuery = useGetUserProfile()
const { data: profile } = profileQuery
const { mutate: deleteRound } = useDeleteRound()
const { mutate: startRound } = useStartRound()
const { mutate: closeSubmissions } = useCloseRoundSubmissions()
const { mutate: markEvaluated } = useMarkRoundEvaluated()
const isConfirmOpen = ref(false)
const pendingAction = ref<'start' | 'close' | 'evaluate' | 'delete' | null>(null)
const isPending = ref(false)

const confirmation = computed(() => {
  switch (pendingAction.value) {
    case 'start':
      return {
        title: 'Start round?',
        message: 'Starting this round opens its submission period for participating teams.',
        confirmText: 'Start round',
      }
    case 'close':
      return {
        title: 'Close submissions?',
        message: 'Teams will no longer be able to submit work for this round.',
        confirmText: 'Close submissions',
      }
    case 'evaluate':
      return {
        title: 'Mark round evaluated?',
        message: 'This marks the round as evaluated and finalizes its results.',
        confirmText: 'Mark evaluated',
      }
    default:
      return {
        title: 'Delete round?',
        message: 'This permanently deletes the round and cannot be undone.',
        confirmText: 'Delete round',
      }
  }
})

function requestConfirmation(action: 'start' | 'close' | 'evaluate' | 'delete') {
  pendingAction.value = action
  isConfirmOpen.value = true
}

function performConfirmedAction() {
  const action = pendingAction.value
  if (!action || isPending.value) return
  isPending.value = true

  const mutation =
    action === 'start'
      ? startRound
      : action === 'close'
        ? closeSubmissions
        : action === 'evaluate'
          ? markEvaluated
          : deleteRound

  mutation(
    { id: props.roundId },
    {
      onSuccess: () => {
        isConfirmOpen.value = false
        pendingAction.value = null
      },
      onError: (error) => {
        isConfirmOpen.value = false
        pendingAction.value = null
        showNotification(error?.message, 'error')
      },
      onSettled: () => {
        isPending.value = false
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
