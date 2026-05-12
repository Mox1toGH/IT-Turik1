<template>
  <ui-modal :model-value="props.modelValue" @update:model-value="toggleOpen" @close="closeModal">
    <template #title>
      <h3>Delete event</h3>
    </template>

    <div>
      <p class="modal-text">
        This action cannot be undone. Enter
        <ui-badge variant="red">{{ props.title }}</ui-badge>
        to confirm deletion.
      </p>

      <ui-input
        v-model="confirmInput"
        :placeholder="props.title"
        style="width: 100%"
        :disabled="isPending"
      />

      <p v-if="errorMessage" class="text-error">
        {{ errorMessage }}
      </p>
    </div>

    <template #footer>
      <ui-button variant="secondary" :disabled="isPending" @click="closeModal"> Cancel </ui-button>

      <ui-button variant="danger" :disabled="!canDelete" @click="handleDelete">
        <loading-icon v-if="isPending" />
        Delete permanently
      </ui-button>
    </template>
  </ui-modal>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiModal from '@/components/ui/UiModal.vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import { useDeleteEvent } from '@/api/queries/tournaments'
import { parseApiError } from '@/api/errors'
import { useNotification } from '@/composables/useNotification'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import { useQueryClient } from '@tanstack/vue-query'
import { tournamentsKeys } from '@/api/queries/keys'
import type { TournamentId } from '@/api/dbTypes'

interface Props {
  modelValue: boolean
  eventId: number
  tournamentId: TournamentId
  title: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
}>()

const confirmInput = ref('')
const errorMessage = ref('')

function closeModal() {
  emit('update:modelValue', false)
  confirmInput.value = ''
  errorMessage.value = ''
}

const { showNotification } = useNotification()
const queryClient = useQueryClient()
const { mutate: deleteEvent, isPending } = useDeleteEvent()
const canDelete = computed(() => {
  return confirmInput.value === props.title && !isPending.value
})

async function handleDelete() {
  if (!canDelete.value) {
    errorMessage.value = `Please enter "${props.title}" exactly.`
    return
  }

  deleteEvent(
    {
      eventId: props.eventId,
    },
    {
      onError: (error) => {
        const parsedError = parseApiError(error)
        showNotification(parsedError?.message, 'error')
      },

      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: tournamentsKeys.events(props.tournamentId) })
        emit('update:modelValue', false)
        showNotification('Event deleted successfully', 'success')
      },
    },
  )
}

const toggleOpen = () => {
  emit('update:modelValue', !props.modelValue)
}
</script>

<style scoped>
.modal-text {
  margin-bottom: 1rem;
}

.text-error {
  color: var(--danger);
  margin-top: 0.75rem;
}
</style>
