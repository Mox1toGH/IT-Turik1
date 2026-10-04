<template>
  <ui-modal v-model="isDeleteModalOpen" :close-on-backdrop="!isDeleting">
    <template #title>
      <h3>Delete tournament</h3>
    </template>

    <div>
      <p class="modal-text">
        This action cannot be undone. Enter
        <ui-badge :title="tournament?.name" variant="red">{{
          truncateText(tournament?.name || `Tournament ${props.tournamentId}`, 15)
        }}</ui-badge>
        to confirm.
      </p>

      <ui-input
        v-model="deleteConfirmInput"
        :placeholder="tournament?.name"
        :disabled="isDeleting"
        style="width: 100%"
      />

      <p v-if="deleteError" class="text-error">{{ deleteError }}</p>
    </div>

    <template #footer>
      <ui-button
        variant="secondary"
        size="sm"
        :disabled="isDeleting"
        @click="isDeleteModalOpen = false"
      >
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
import { useDeleteTournament, useGetTournament } from '@/api/tournaments/tournaments'
import { useRouter } from 'vue-router'

interface Props {
  tournamentId: number
}

const props = defineProps<Props>()

const isDeleteModalOpen = defineModel({ default: false })
const deleteConfirmInput = ref('')
const deleteError = ref('')

const { data: tournament } = useGetTournament(props.tournamentId)

const canDeleteTournament = computed(
  () => deleteConfirmInput.value === tournament.value?.name && !isDeleting.value,
)

const router = useRouter()
const { showNotification, hideNotification } = useNotification()
const { mutate: deleteTournament, isPending: isDeleting } = useDeleteTournament()

const handleDeleteTournament = () => {
  if (!canDeleteTournament.value) {
    deleteError.value = `Please enter "${tournament.value?.name}" exactly.`
    return
  }

  deleteError.value = ''
  hideNotification()

  deleteTournament(
    { id: props.tournamentId },
    {
      onSuccess: () => {
        isDeleteModalOpen.value = false
        showNotification('Tournament deleted successfully.', 'success')
        router.push('/tournaments')
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
