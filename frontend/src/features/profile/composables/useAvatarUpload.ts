import { computed, ref, watch, type ComputedRef, type Ref } from 'vue'
import { useNotification } from '@/composables/useNotification'
import {
  clearImagePosition,
  readImagePosition,
  toObjectPosition,
  writeImagePosition,
} from '@/lib/imagePosition'
import { useDeleteUserAvatar, useUpdateUserAvatar } from '@/api/accounts/accounts'
import type { UserSummary } from '@/shared/types/user'

export interface UseAvatarUploadReturn {
  isOpen: Ref<boolean>
  selectedAvatar: Ref<File[]>
  previewUrl: ComputedRef<string>
  previewObjectPosition: ComputedRef<string>
  isUpdating: ComputedRef<boolean>
  open: () => void
  closeModal: () => void
  resetState: () => void
  removeAvatar: () => void
  saveAvatar: () => void
  onPreviewPointerDown: (event: PointerEvent) => void
}

export function useAvatarUpload(
  user: Ref<Pick<UserSummary, 'id' | 'avatar'> | undefined>,
  disabled: Ref<boolean>,
): UseAvatarUploadReturn {
  const isOpen = ref(false)
  const selectedAvatar = ref<File[]>([])
  const selectedAvatarUrl = ref('')
  const avatarPositionKey = computed(() =>
    user.value?.id ? `image-position:avatar:user:${user.value.id}` : '',
  )
  const positionX = ref(50)
  const positionY = ref(50)

  const previewUrl = computed(() => {
    if (selectedAvatarUrl.value) return selectedAvatarUrl.value
    return user.value?.avatar || ''
  })
  const previewObjectPosition = computed(() =>
    toObjectPosition({
      x: positionX.value,
      y: positionY.value,
    }),
  )

  const { showNotification } = useNotification()
  const { mutate: updateAvatar, isPending: isUpdatingAvatar } = useUpdateUserAvatar()
  const { mutate: removeAvatarRequest, isPending: isRemovingAvatar } = useDeleteUserAvatar()
  const isUpdating = computed(() => isUpdatingAvatar.value || isRemovingAvatar.value)

  const open = (): void => {
    if (!disabled.value) isOpen.value = true
  }

  const closeModal = (): void => {
    isOpen.value = false
  }

  const resetState = (): void => {
    selectedAvatar.value = []
    const saved = readImagePosition(avatarPositionKey.value)
    positionX.value = saved.x
    positionY.value = saved.y
    if (selectedAvatarUrl.value) {
      URL.revokeObjectURL(selectedAvatarUrl.value)
      selectedAvatarUrl.value = ''
    }
    closeModal()
  }

  const removeAvatar = (): void => {
    removeAvatarRequest(void 0, {
      onSuccess: async () => {
        clearImagePosition(avatarPositionKey.value)
        showNotification('Avatar removed.', 'success')
        resetState()
      },
      onError: (error) => {
        showNotification(error.message, 'error')
      },
    })
  }

  const saveAvatar = (): void => {
    if (!user.value) return

    const avatar = selectedAvatar.value[0]
    if (!avatar) return

    updateAvatar(
      { data: { avatar } },
      {
        onSuccess: async () => {
          if (avatarPositionKey.value) {
            writeImagePosition(avatarPositionKey.value, { x: positionX.value, y: positionY.value })
          }
          showNotification('Avatar updated.', 'success')
          resetState()
        },
        onError: (error) => {
          showNotification(error.message, 'error')
        },
      },
    )
  }

  const onPreviewPointerDown = (event: PointerEvent): void => {
    const target = event.currentTarget as HTMLElement | null
    if (!target) return
    target.setPointerCapture(event.pointerId)

    const applyPositionFromPointer = (pointerEvent: PointerEvent): void => {
      const rect = target.getBoundingClientRect()
      if (!rect.width || !rect.height) return
      positionX.value = ((pointerEvent.clientX - rect.left) / rect.width) * 100
      positionY.value = ((pointerEvent.clientY - rect.top) / rect.height) * 100
    }

    applyPositionFromPointer(event)

    const handleMove = (pointerEvent: PointerEvent): void => applyPositionFromPointer(pointerEvent)
    const handleUp = (pointerEvent: PointerEvent): void => {
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

  watch(selectedAvatar, (files) => {
    const firstFile = files[0]

    if (selectedAvatarUrl.value) {
      URL.revokeObjectURL(selectedAvatarUrl.value)
      selectedAvatarUrl.value = ''
    }
    if (firstFile) {
      selectedAvatarUrl.value = URL.createObjectURL(firstFile)
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

  return {
    isOpen,
    selectedAvatar,
    previewUrl,
    previewObjectPosition,
    isUpdating,
    open,
    closeModal,
    resetState,
    removeAvatar,
    saveAvatar,
    onPreviewPointerDown,
  }
}
