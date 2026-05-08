<template>
  <ui-button :disabled="props.disabled" size="sm" variant="danger" @click="isDeleteModalOpen = true"
    >Delete team</ui-button
  >

  <ui-modal v-model="isDeleteModalOpen" :close-on-backdrop="!isDeleting">
    <template #title>
      <h3>Delete team</h3>
    </template>

    <div>
      <p class="modal-text">
        This action cannot be undone. Enter
        <ui-badge :title="props.team?.name" variant="red">{{
          truncateText(props.team?.name ?? '', 15)
        }}</ui-badge>
        to confirm.
      </p>

      <ui-input
        v-model="deleteConfirmInput"
        :placeholder="props.team?.name"
        :disabled="isDeleting"
        style="width: 100%"
      />

      <p v-if="deleteError" class="text-error">{{ deleteError }}</p>
    </div>

    <template #footer>
      <ui-button variant="secondary" size="sm" :disabled="isDeleting" @click="closeDeleteModal">
        Cancel
      </ui-button>

      <ui-button variant="danger" size="sm" :disabled="!canDeleteTeam" @click="handleDeleteTeam">
        <loading-icon v-if="isDeleting" />
        Delete permanently
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
import type { GetTeamInfoResponse } from '@/api/services/teams/types'
import { computed, ref } from 'vue'
import { useDeleteTeam } from '@/api/queries/teams'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import { truncateText } from '@/lib/utils'

interface Props {
  team?: GetTeamInfoResponse
  disabled?: boolean
}

const props = defineProps<Props>()
const { hideNotification } = useNotification()

const { mutate: deleteTeam, isPending: isDeleting } = useDeleteTeam()

const emit = defineEmits<{
  (e: 'deleted'): void
}>()

const isDeleteModalOpen = ref(false)
const deleteConfirmInput = ref('')
const deleteError = ref('')

const canDeleteTeam = computed(
  () => deleteConfirmInput.value === props.team?.name && !isDeleting.value,
)

function closeDeleteModal() {
  isDeleteModalOpen.value = false
}

const handleDeleteTeam = async () => {
  if (!props.team) return

  if (!canDeleteTeam.value) {
    deleteError.value = `Please enter "${props.team?.name}" exactly.`
    return
  }

  deleteError.value = ''
  hideNotification()

  deleteTeam(
    { id: props.team.id },
    {
      onSuccess: () => {
        closeDeleteModal()
        emit('deleted')
      },
      onError: (err) => {
        deleteError.value = err.response ? 'Unable to delete team.' : 'Server connection error.'
      },
    },
  )
}
</script>

<style scoped>
.modal-text {
  margin-bottom: 1rem;
  color: var(--muted-foreground);
}
</style>
