import { computed, ref, watch, type ComputedRef, type Ref } from 'vue'
import { useNotification } from '@/composables/useNotification'
import {
  clearImagePosition,
  readImagePosition,
  toObjectPosition,
  writeImagePosition,
} from '@/lib/imagePosition'
import { useDeleteTeamBanner, useTeamBannerUpdate } from '@/api/teams/teams'
import type { TeamResponse } from '@/api/backendAPINinja.schemas'

export interface UseTeamBannerReturn {
  isBannerModalOpen: Ref<boolean>
  selectedBanner: Ref<File[]>
  bannerPreviewUrl: ComputedRef<string>
  bannerObjectPosition: ComputedRef<string>
  heroBannerStyle: ComputedRef<Record<string, string>>
  isBannerUpdating: ComputedRef<boolean>
  closeBannerModal: () => void
  resetBannerState: () => void
  saveBanner: () => void
  removeBanner: () => void
  onBannerPreviewPointerDown: (event: PointerEvent) => void
}

export function useTeamBanner(
  teamId: number,
  team: Ref<TeamResponse | undefined>,
): UseTeamBannerReturn {
  const isBannerModalOpen = ref(false)
  const selectedBanner = ref<File[]>([])
  const selectedBannerUrl = ref('')
  const bannerPositionX = ref(50)
  const bannerPositionY = ref(50)
  const { showNotification } = useNotification()

  const { mutate: updateBanner, isPending: isUpdatingBanner } = useTeamBannerUpdate()
  const { mutate: removeTeamBanner, isPending: isRemovingBanner } = useDeleteTeamBanner()
  const isBannerUpdating = computed(() => isUpdatingBanner.value || isRemovingBanner.value)

  const bannerPreviewUrl = computed(() => {
    if (selectedBannerUrl.value) return selectedBannerUrl.value
    return team.value?.banner || ''
  })
  const bannerPositionKey = computed(() => `image-position:banner:team:${teamId}`)
  const bannerObjectPosition = computed(() =>
    toObjectPosition({ x: bannerPositionX.value, y: bannerPositionY.value }),
  )

  const heroBannerStyle = computed((): Record<string, string> => {
    if (!team.value?.banner) return {}
    return {
      backgroundImage: `url(${team.value.banner})`,
      backgroundPosition: bannerObjectPosition.value,
    }
  })

  const closeBannerModal = (): void => {
    isBannerModalOpen.value = false
  }

  const resetBannerState = (): void => {
    selectedBanner.value = []
    const saved = readImagePosition(bannerPositionKey.value)
    bannerPositionX.value = saved.x
    bannerPositionY.value = saved.y
    if (selectedBannerUrl.value) {
      URL.revokeObjectURL(selectedBannerUrl.value)
      selectedBannerUrl.value = ''
    }
    closeBannerModal()
  }

  const saveBanner = (): void => {
    const banner = selectedBanner.value[0]
    if (!banner) return

    writeImagePosition(bannerPositionKey.value, {
      x: bannerPositionX.value,
      y: bannerPositionY.value,
    })

    updateBanner(
      { pk: teamId, data: { banner } },
      {
        onSuccess: () => {
          showNotification('Banner updated.', 'success')
          resetBannerState()
        },
        onError: (error) => {
          showNotification(error.message, 'error')
        },
      },
    )
  }

  const removeBanner = (): void => {
    removeTeamBanner(
      { pk: teamId },
      {
        onSuccess: () => {
          clearImagePosition(bannerPositionKey.value)
          showNotification('Banner removed.', 'success')
          resetBannerState()
        },
        onError: (error) => {
          showNotification(error.message, 'error')
        },
      },
    )
  }

  const onBannerPreviewPointerDown = (event: PointerEvent): void => {
    const target = event.currentTarget as HTMLElement | null
    if (!target) return
    target.setPointerCapture(event.pointerId)

    const applyPositionFromPointer = (pointerEvent: PointerEvent): void => {
      const rect = target.getBoundingClientRect()
      if (!rect.width || !rect.height) return
      bannerPositionX.value = ((pointerEvent.clientX - rect.left) / rect.width) * 100
      bannerPositionY.value = ((pointerEvent.clientY - rect.top) / rect.height) * 100
    }

    applyPositionFromPointer(event)

    const handleMove = (pointerEvent: PointerEvent): void => applyPositionFromPointer(pointerEvent)
    const handleUp = (pointerEvent: PointerEvent): void => {
      applyPositionFromPointer(pointerEvent)
      writeImagePosition(bannerPositionKey.value, {
        x: bannerPositionX.value,
        y: bannerPositionY.value,
      })
      target.removeEventListener('pointermove', handleMove)
      target.removeEventListener('pointerup', handleUp)
      target.removeEventListener('pointercancel', handleUp)
    }

    target.addEventListener('pointermove', handleMove)
    target.addEventListener('pointerup', handleUp)
    target.addEventListener('pointercancel', handleUp)
  }

  watch(selectedBanner, (files) => {
    const firstFile = files[0]

    if (selectedBannerUrl.value) {
      URL.revokeObjectURL(selectedBannerUrl.value)
      selectedBannerUrl.value = ''
    }
    if (firstFile) {
      selectedBannerUrl.value = URL.createObjectURL(firstFile)
    }
  })

  watch(
    bannerPositionKey,
    (key) => {
      const saved = readImagePosition(key)
      bannerPositionX.value = saved.x
      bannerPositionY.value = saved.y
    },
    { immediate: true },
  )

  return {
    isBannerModalOpen,
    selectedBanner,
    bannerPreviewUrl,
    bannerObjectPosition,
    heroBannerStyle,
    isBannerUpdating,
    closeBannerModal,
    resetBannerState,
    saveBanner,
    removeBanner,
    onBannerPreviewPointerDown,
  }
}
