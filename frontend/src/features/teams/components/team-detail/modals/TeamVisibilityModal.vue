<template>
  <ui-button
    size="sm"
    variant="warning"
    :disabled="isChangingVisibility"
    @click="toggleVisibilityModal"
  >
    Change visibility
  </ui-button>

  <ui-modal
    v-model="isVisibilityModalOpen"
    :close-on-backdrop="!isChangingVisibility"
    :show-close="!isChangingVisibility"
  >
    <template #title>
      <h3>Change team visibility</h3>
    </template>

    <div>
      <p class="modal-text">
        Select the new visibility for
        <ui-badge variant="green" :title="team?.name">{{
          truncateText(team?.name ?? '', 15)
        }}</ui-badge
        ><br />
        This affects who can discover and join your team.
      </p>

      <div class="visibility-options">
        <label class="visibility-option" :class="{ selected: selectedVisibility === true }">
          <ui-input
            type="radio"
            name="visibility"
            :value="true"
            :checked="selectedVisibility === true"
            :disabled="isChangingVisibility"
            @change="selectedVisibility = true"
          />
          <div class="visibility-option-content">
            <div class="visibility-option-header">
              <eye-in-circle />
              <strong>Public</strong>
            </div>
            <p class="visibility-subtext">Anyone can find and request to join this team.</p>
          </div>
        </label>

        <label class="visibility-option" :class="{ selected: selectedVisibility === false }">
          <ui-input
            type="radio"
            name="visibility"
            :value="false"
            :checked="selectedVisibility === false"
            :disabled="isChangingVisibility"
            @change="selectedVisibility = false"
          />
          <div class="visibility-option-content">
            <div class="visibility-option-header">
              <lock-icon />
              <strong>Private</strong>
            </div>
            <p>Only invited members can find and access this team.</p>
          </div>
        </label>
      </div>

      <div v-if="selectedVisibility !== team?.is_public" class="visibility-confirm-note">
        <danger-icon />
        <span>
          You are about to change this team from
          <strong>{{ team?.is_public ? 'Public' : 'Private' }}</strong>
          to
          <strong>{{ selectedVisibility ? 'Public' : 'Private' }}</strong
          >.
        </span>
      </div>

      <p v-if="changeVisibilityError?.message" class="text-error modal-error">
        {{ changeVisibilityError.message }}
      </p>
    </div>

    <template #footer>
      <ui-button
        size="sm"
        variant="secondary"
        type="button"
        :disabled="isChangingVisibility"
        @click="toggleVisibilityModal"
      >
        Cancel
      </ui-button>
      <ui-button
        variant="warning"
        size="sm"
        type="button"
        :disabled="isChangingVisibility || selectedVisibility === team?.is_public"
        @click="confirmChangeVisibility"
      >
        <loading-icon v-if="isChangingVisibility" size="sm" />
        Confirm change
      </ui-button>
    </template>
  </ui-modal>
</template>

<script setup lang="ts">
import UiBadge from '@/components/ui/UiBadge.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiModal from '@/components/ui/UiModal.vue'
import { useNotification } from '@/composables/useNotification'
import DangerIcon from '@/icons/DangerIcon.vue'
import EyeInCircle from '@/icons/EyeInCircle.vue'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import LockIcon from '@/icons/LockIcon.vue'
import type { GetTeamInfoResponse } from '@/api/services/teams/types'
import { computed, ref } from 'vue'
import { useChangeTeamVisibility } from '@/api/queries/teams'
import { parseApiError } from '@/api/errors'
import { truncateText } from '@/lib/utils'

interface Props {
  team?: GetTeamInfoResponse
}

const emit = defineEmits<{
  (e: 'changedTeamVisibility', newTeamValue: GetTeamInfoResponse): void
}>()

const props = defineProps<Props>()
const { showNotification, hideNotification } = useNotification()

const selectedVisibility = ref(props.team?.is_public)
const isVisibilityModalOpen = ref(false)

const toggleVisibilityModal = () => {
  isVisibilityModalOpen.value = !isVisibilityModalOpen.value
}

const {
  mutate: changeTeamVisibility,
  isPending: isChangingVisibility,
  error,
} = useChangeTeamVisibility()
const changeVisibilityError = computed(() => parseApiError(error.value))

const confirmChangeVisibility = async () => {
  if (!props.team?.id || selectedVisibility.value === undefined) return

  hideNotification()

  changeTeamVisibility(
    { teamId: props.team.id, body: { is_public: selectedVisibility.value } },
    {
      onSuccess: (data) => {
        showNotification(
          `Team visibility changed to ${props.team?.is_public ? 'Public' : 'Private'}.`,
          'success',
        )
        emit('changedTeamVisibility', data)

        toggleVisibilityModal()
      },
      onError: (err) => {
        showNotification(
          err.response ? 'Unable to change team visibility.' : 'Unable to change team visibility.',
          'error',
        )
      },
    },
  )
}
</script>

<style scoped>
.visibility-options {
  display: grid;
  gap: 0.6rem;
  margin: 1rem 0 0.8rem;
}

.visibility-option {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.75rem 0.9rem;
  border: 1.5px solid var(--line-soft);
  border-radius: 10px;
  cursor: pointer;
  transition:
    border-color 0.15s,
    background 0.15s;
}

.visibility-option:hover {
  border-color: var(--brand-500, #14b8a6);
  background: rgba(20, 184, 166, 0.04);
}

.visibility-option.selected {
  border-color: var(--brand-500, #14b8a6);
  background: rgba(20, 184, 166, 0.06);
}

.visibility-option-content {
  flex: 1;
}

.visibility-option-content p {
  margin: 0.2rem 0 0;
  font-size: 0.84rem;
}

.visibility-option-header {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.visibility-option-icon {
  width: 1rem;
  height: 1rem;
  color: var(--color-gray-600);
}

.danger-zone-icon {
  width: 0.95rem;
  height: 0.95rem;
  flex-shrink: 0;
}

.visibility-confirm-note {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 0.8rem;
  background: color-mix(in srgb, var(--warning) 10%, transparent);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 8px;
  font-size: 0.87rem;
  color: var(--warning);
  margin-bottom: 0.5rem;
}

.modal-text,
.visibility-subtext {
  color: var(--muted-foreground);
}
</style>
