<template>
  <button class="avatar-edit-btn" type="button" @click="isOpen = true" :disabled="disabled">
    <AvatarEditIcon />
  </button>

  <ui-modal v-model="isOpen" @close="resetState">
    <template #title>
      <h3>Avatar</h3>
    </template>

    <div class="modal-body">
      <div
        v-if="previewUrl"
        class="avatar-preview-frame"
        @pointerdown="onPreviewPointerDown"
      >
        <img
          :src="previewUrl"
          alt="Avatar preview"
          class="avatar-preview"
          :style="{ objectPosition: previewObjectPosition }"
        />
      </div>
      <div v-else class="avatar-empty">No avatar</div>

      <p v-if="previewUrl" class="position-hint">Drag image to choose avatar position</p>
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
import { clearImagePosition, readImagePosition, toObjectPosition, writeImagePosition } from '@/lib/imagePosition'

const props = defineProps<{
  user?: User
  disabled?: boolean
}>()

const isOpen = ref(false)
const selectedAvatar = ref<File | null>(null)
const selectedAvatarUrl = ref('')
const avatarPositionKey = computed(() => (props.user?.id ? `image-position:avatar:user:${props.user.id}` : ''))
const positionX = ref(50)
const positionY = ref(50)

const previewUrl = computed(() => {
  if (selectedAvatarUrl.value) return selectedAvatarUrl.value
  return props.user?.avatar || ''
})
const previewObjectPosition = computed(() =>
  toObjectPosition({
    x: positionX.value,
    y: positionY.value,
  }),
)

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
  const saved = readImagePosition(avatarPositionKey.value)
  positionX.value = saved.x
  positionY.value = saved.y
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
      clearImagePosition(avatarPositionKey.value)
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
        if (avatarPositionKey.value) {
          writeImagePosition(avatarPositionKey.value, { x: positionX.value, y: positionY.value })
        }
        showNotification('Avatar updated.', 'success')
        resetState()
      },
      onError: () => {
        showNotification('Failed to update avatar.', 'error')
      },
    },
  )
}

const onPreviewPointerDown = (event: PointerEvent) => {
  const target = event.currentTarget as HTMLElement | null
  if (!target) return
  target.setPointerCapture(event.pointerId)

  const applyPositionFromPointer = (pointerEvent: PointerEvent) => {
    const rect = target.getBoundingClientRect()
    if (!rect.width || !rect.height) return
    positionX.value = ((pointerEvent.clientX - rect.left) / rect.width) * 100
    positionY.value = ((pointerEvent.clientY - rect.top) / rect.height) * 100
  }

  applyPositionFromPointer(event)

  const handleMove = (pointerEvent: PointerEvent) => applyPositionFromPointer(pointerEvent)
  const handleUp = (pointerEvent: PointerEvent) => {
    applyPositionFromPointer(pointerEvent)
    target.removeEventListener('pointermove', handleMove)
    target.removeEventListener('pointerup', handleUp)
    target.removeEventListener('pointercancel', handleUp)
    if (avatarPositionKey.value) {
      writeImagePosition(avatarPositionKey.value, { x: positionX.value, y: positionY.value })
    }
  }

  target.addEventListener('pointermove', handleMove)
  target.addEventListener('pointerup', handleUp)
  target.addEventListener('pointercancel', handleUp)
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

watch(
  avatarPositionKey,
  (key) => {
    const saved = readImagePosition(key)
    positionX.value = saved.x
    positionY.value = saved.y
  },
  { immediate: true },
)
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

.avatar-preview-frame,
.avatar-empty {
  width: 120px;
  height: 120px;
  border-radius: 999px;
  border: 1px solid var(--line-soft);
}

.avatar-preview-frame {
  overflow: hidden;
  cursor: move;
}

.position-hint {
  margin: 0;
  color: var(--color-gray-500);
  font-size: 0.8rem;
}

.avatar-preview,
.avatar-empty {
  width: 100%;
  height: 100%;
}

.avatar-preview {
  object-fit: cover;
  user-select: none;
  pointer-events: none;
}

.avatar-empty {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--color-gray-500);
  font-size: 0.85rem;
}
</style>
