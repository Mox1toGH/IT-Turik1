import { computed, onBeforeUnmount, ref, toValue, watch, type MaybeRefOrGetter, type Ref } from 'vue'
import { useQueryClient } from '@tanstack/vue-query'
import { useNotification } from '@/composables/useNotification'
import { useBannerPosition } from './useBannerPosition'
import {
  getGetTournamentQueryKey,
  useDeleteTournamentBanner,
  useGetTournament,
  useUpdateTournamentBanner,
} from '@/api/tournaments/tournaments'

export interface BannerPosition {
  x: number
  y: number
}

const PREVIEW_MAX_SIZE = 1600

async function createPreviewUrl(file: File): Promise<string> {
  try {
    const bitmap = await createImageBitmap(file)
    const scale = Math.min(1, PREVIEW_MAX_SIZE / Math.max(bitmap.width, bitmap.height))

    const canvas = document.createElement('canvas')
    canvas.width = Math.round(bitmap.width * scale)
    canvas.height = Math.round(bitmap.height * scale)
    canvas.getContext('2d')?.drawImage(bitmap, 0, 0, canvas.width, canvas.height)
    bitmap.close()

    const blob = await new Promise<Blob | null>((resolve) =>
      canvas.toBlob(resolve, 'image/webp', 0.85),
    )

    return URL.createObjectURL(blob ?? file)
  } catch {
    return URL.createObjectURL(file)
  }
}

export function useBannerUpload(
  tournamentId: MaybeRefOrGetter<number>,
  isOpen: Ref<boolean>,
) {
  const id = computed<number>(() => toValue(tournamentId))
  const selectedBanner = ref<File[]>([])
  const selectedBannerUrl = ref<string>('')

  const queryClient = useQueryClient()
  const { showNotification } = useNotification()
  const { data: tournament } = useGetTournament(id)
  const { mutate: updateBanner, isPending: isUpdatingBanner } = useUpdateTournamentBanner()
  const { mutate: removeTournamentBanner, isPending: isRemovingBanner } =
    useDeleteTournamentBanner()

  const { position, save: savePosition, clear: clearPosition } = useBannerPosition(id.value)

  const draft = ref<BannerPosition>({ ...position.value })

  const positionChanged = computed<boolean>(
    () => draft.value.x !== position.value.x || draft.value.y !== position.value.y,
  )
  const canSave = computed<boolean>(
    () => selectedBanner.value.length > 0 || positionChanged.value,
  )
  const isBannerUpdating = computed<boolean>(
    () => isUpdatingBanner.value || isRemovingBanner.value,
  )
  const bannerPreviewUrl = computed<string>(
    () => selectedBannerUrl.value || tournament.value?.banner || '',
  )

  let previewToken = 0

  const revokePreviewUrl = (): void => {
    if (selectedBannerUrl.value) {
      URL.revokeObjectURL(selectedBannerUrl.value)
      selectedBannerUrl.value = ''
    }
  }

  watch(selectedBanner, async (files) => {
    revokePreviewUrl()
    const file = files[0]
    const token = ++previewToken
    if (!file) return

    const url = await createPreviewUrl(file)
    if (token !== previewToken) {
      URL.revokeObjectURL(url)
      return
    }
    selectedBannerUrl.value = url
  })

  watch(bannerPreviewUrl, () => {
    // Preview source changed; BannerPreview resets its own measurements.
  })

  const refreshTournament = (): Promise<unknown> =>
    queryClient.invalidateQueries({ queryKey: getGetTournamentQueryKey(id.value) })

  const resetBannerState = (): void => {
    previewToken++
    selectedBanner.value = []
    draft.value = { ...position.value }
    revokePreviewUrl()
  }

  const cancel = (): void => {
    resetBannerState()
    isOpen.value = false
  }

  const saveBanner = (): void => {
    const banner = selectedBanner.value[0]
    if (!tournament.value) return

    if (!banner) {
      savePosition(draft.value)
      showNotification('Banner position saved.', 'success')
      isOpen.value = false
      return
    }

    updateBanner(
      { id: tournament.value.id, data: { banner } },
      {
        onSuccess: async () => {
          await refreshTournament()
          savePosition(draft.value)
          showNotification('Banner updated.', 'success')
          resetBannerState()
          isOpen.value = false
        },
        onError: (error) => showNotification(error.message, 'error'),
      },
    )
  }

  const removeBanner = (): void => {
    if (!tournament.value) return

    removeTournamentBanner(
      { id: tournament.value.id },
      {
        onSuccess: async () => {
          clearPosition()
          await refreshTournament()
          showNotification('Banner removed.', 'success')
          resetBannerState()
        },
        onError: (error) => showNotification(error.message, 'error'),
      },
    )
  }

  onBeforeUnmount(() => {
    previewToken++
    revokePreviewUrl()
  })

  return {
    tournament,
    selectedBanner,
    selectedBannerUrl,
    draft,
    positionChanged,
    canSave,
    isBannerUpdating,
    bannerPreviewUrl,
    resetBannerState,
    cancel,
    saveBanner,
    removeBanner,
  }
}
