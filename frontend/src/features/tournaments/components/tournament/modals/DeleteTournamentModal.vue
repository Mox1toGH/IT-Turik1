<template>
  <ui-modal v-model="isDeleteModalOpen" :close-on-backdrop="!isDeleting">
    <template #title>
      <h3>Delete tournament</h3>
    </template>

    <div>
      <p class="modal-text">
        Permanently delete this <ui-badge variant="red">tournament</ui-badge> and
        <ui-badge variant="red">ALL associated data</ui-badge>. Enter the tournament name to
        confirm.
      </p>

      <ui-query-block :query="tournamentQuery">
        <template #error><p class="text-error">Could not load tournament details.</p></template>
        <ui-query-field>
          <template #skeleton><ui-skeleton variant="rect" width="100%" height="40px" /></template>
          <div class="delete-confirmation">
            <ui-badge :title="tournament?.name" variant="red">{{
              truncateText(tournament?.name || `Tournament ${props.tournamentId}`, 15)
            }}</ui-badge>
            <ui-input
              v-model="deleteConfirmInput"
              :placeholder="tournament?.name"
              :disabled="isDeleting"
              style="width: 100%"
            />
          </div>
        </ui-query-field>
      </ui-query-block>

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
        <LoaderCircle class="animate-spin" v-if="isDeleting" />
        Delete permanently
      </ui-button>
    </template>
  </ui-modal>
</template>

<script setup lang="ts">
import UiBadge from '@/components/ui/UiBadge'
import UiButton from '@/components/ui/UiButton'
import UiInput from '@/components/ui/UiInput'
import UiModal from '@/components/ui/UiModal'
import { UiQueryBlock, UiQueryField } from '@/components/query'
import UiSkeleton from '@/components/ui/UiSkeleton'
import { useNotification } from '@/composables/useNotification'
import { computed, ref } from 'vue'
import { LoaderCircle } from 'lucide-vue-next'
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

const tournamentQuery = useGetTournament(props.tournamentId)
const { data: tournament } = tournamentQuery

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

.delete-confirmation {
  display: grid;
  gap: 0.5rem;
}
</style>
