<template>
  <ui-button :disabled="props.disabled" size="sm" variant="danger" @click="isDeleteModalOpen = true"
    >Delete</ui-button
  >

  <ui-modal v-model="isDeleteModalOpen" :close-on-backdrop="!isDeleting">
    <template #title>
      <h3>Delete tournament</h3>
    </template>

    <div>
      <p class="modal-text">
        This action cannot be undone. Enter
        <ui-badge :title="props.tournamentName" variant="red">{{
          truncateText(props.tournamentName, 15)
        }}</ui-badge>
        to confirm.
      </p>

      <ui-input
        v-model="deleteConfirmInput"
        :placeholder="props.tournamentName"
        :disabled="isDeleting"
        style="width: 100%"
      />

      <p v-if="deleteError" class="text-error">{{ deleteError }}</p>
    </div>

    <template #footer>
      <ui-button variant="secondary" size="sm" :disabled="isDeleting" @click="closeDeleteModal">
        Cancel
      </ui-button>

      <ui-button
        variant="danger"
        size="sm"
        :disabled="!canDeleteTournament"
        @click="handleDeleteTournament"
      >
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
import { computed, ref } from 'vue'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import { truncateText } from '@/lib/utils'
import { useDeleteTournament } from '@/api/tournaments/tournaments'

interface Props {
  tournamentId: number
  tournamentName: string
  disabled?: boolean
}

const props = defineProps<Props>()
const { hideNotification } = useNotification()

const { mutate: deleteTournament, isPending: isDeleting } = useDeleteTournament()

const emit = defineEmits<{
  (e: 'deleted'): void
}>()

const { showNotification } = useNotification()

const isDeleteModalOpen = ref(false)
const deleteConfirmInput = ref('')
const deleteError = ref('')

const canDeleteTournament = computed(
  () => deleteConfirmInput.value === props.tournamentName && !isDeleting.value,
)

function closeDeleteModal() {
  isDeleteModalOpen.value = false
}

const handleDeleteTournament = () => {
  if (!canDeleteTournament.value) {
    deleteError.value = `Please enter "${props.tournamentName}" exactly.`
    return
  }

  deleteError.value = ''
  hideNotification()

  deleteTournament(
    { id: props.tournamentId },
    {
      onSuccess: () => {
        closeDeleteModal()
        emit('deleted')
      },
      onError: (error) => {
        deleteError.value = error.message

        showNotification(error.message, 'error')
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
