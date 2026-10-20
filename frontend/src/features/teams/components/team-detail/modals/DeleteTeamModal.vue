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
import { useNotification } from '@/composables/useNotification'
import { computed, ref } from 'vue'
import { LoaderCircle } from 'lucide-vue-next'
import { truncateText } from '@/lib/utils'
import { useDeleteTeam } from '@/api/teams/teams'
import type { Team } from '@/features/teams/types'
interface Props {
  team?: Team
  disabled?: boolean
}

const props = defineProps<Props>()
const { showNotification, hideNotification } = useNotification()

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
    { pk: props.team.id },
    {
      onSuccess: () => {
        closeDeleteModal()
        emit('deleted')
      },
      onError: (error) => {
        deleteError.value = error.message
        showNotification(error.message)
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
