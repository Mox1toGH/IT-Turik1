<template>
  <button class="avatar-edit-btn" type="button" @click="isOpen = true" :disabled="disabled">
    <AvatarEditIcon />
  </button>

  <ui-modal v-model="isOpen" @close="resetState">
    <template #title>
      <h3>Avatar</h3>
    </template>

    <div class="modal-body">
      <img v-if="previewUrl" :src="previewUrl" alt="Avatar preview" class="avatar-preview" />
      <div v-else class="avatar-empty">No avatar</div>

      <input type="file" accept="image/*" @change="onAvatarChange" />
    </div>

    <template #footer>
      <ui-button size="sm" variant="secondary" @click="resetState">Cancel</ui-button>
      <ui-button
        size="sm"
        variant="secondary"
        :disabled="isUpdating || !previewUrl"
        @click="removeAvatar"
      >
        Remove
      </ui-button>
      <ui-button size="sm" :disabled="isUpdating" @click="saveAvatar">
        <LoadingIcon v-if="isUpdating" />
        Save
      </ui-button>
    </template>
  </ui-modal>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useQueryClient } from '@tanstack/vue-query'
import UiModal from '@/components/ui/UiModal.vue'
import UiButton from '@/components/ui/UiButton.vue'
import AvatarEditIcon from '@/icons/AvatarEditIcon.vue'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import { useNotification } from '@/composables/useNotification'
import { useRemoveAvatar, useUpdateAvatar } from '@/api/queries/accounts'
import { accountKeys } from '@/api/queries/keys'
import type { User } from '@/api/dbTypes'

const props = defineProps<{
  user?: User
  disabled?: boolean
}>()

const isOpen = ref(false)
const selectedAvatar = ref<File | null>(null)
const selectedAvatarUrl = ref('')

const previewUrl = computed(() => {
  if (selectedAvatarUrl.value) return selectedAvatarUrl.value
  return props.user?.avatar || ''
})

const { showNotification } = useNotification()
const queryClient = useQueryClient()
const { mutate: updateAvatar, isPending: isUpdatingAvatar } = useUpdateAvatar()
const { mutate: removeAvatarRequest, isPending: isRemovingAvatar } = useRemoveAvatar()
const isUpdating = computed(() => isUpdatingAvatar.value || isRemovingAvatar.value)

const closeModal = () => {
  isOpen.value = false
}

const resetState = () => {
  selectedAvatar.value = null
  if (selectedAvatarUrl.value) {
    URL.revokeObjectURL(selectedAvatarUrl.value)
    selectedAvatarUrl.value = ''
  }
  closeModal()
}

const onAvatarChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  selectedAvatar.value = target.files?.[0] || null
}

const removeAvatar = () => {
  removeAvatarRequest(void 0, {
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: accountKeys.profile() })
      showNotification('Avatar removed.', 'success')
      resetState()
    },
    onError: () => {
      showNotification('Failed to remove avatar.', 'error')
    },
  })
}

const saveAvatar = () => {
  if (!props.user) return

  if (!selectedAvatar.value) return

  updateAvatar(
    { file: selectedAvatar.value },
    {
      onSuccess: async () => {
        await queryClient.invalidateQueries({ queryKey: accountKeys.profile() })
        showNotification('Avatar updated.', 'success')
        resetState()
      },
      onError: () => {
        showNotification('Failed to update avatar.', 'error')
      },
    },
  )
}

watch(selectedAvatar, (file) => {
  if (selectedAvatarUrl.value) {
    URL.revokeObjectURL(selectedAvatarUrl.value)
    selectedAvatarUrl.value = ''
  }
  if (file) {
    selectedAvatarUrl.value = URL.createObjectURL(file)
  }
})
</script>

<style scoped>
.avatar-edit-btn {
  width: 2rem;
  height: 2rem;
  border-radius: 999px;
  border: 1px solid var(--line-soft);
  background: #fff;
  color: var(--color-gray-700);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.avatar-edit-btn:hover {
  border-color: var(--brand-500);
  color: var(--brand-700);
}

.modal-body {
  display: grid;
  gap: 0.75rem;
}

.avatar-preview,
.avatar-empty {
  width: 120px;
  height: 120px;
  border-radius: 999px;
  border: 1px solid var(--line-soft);
}

.avatar-preview {
  object-fit: cover;
}

.avatar-empty {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--color-gray-500);
  font-size: 0.85rem;
}
</style>
