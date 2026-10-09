<template>
  <ui-modal v-model="isOpen" @close="resetBannerState" scrollable>
    <template #title>
      <h3>Tournament banner</h3>
    </template>

    <div class="banner-modal-body">
      <div
        v-if="bannerPreviewUrl"
        ref="frameRef"
        class="banner-preview-frame"
        :class="{ 'is-dragging': isDragging }"
        @pointerdown.prevent="onBannerPreviewPointerDown"
        @dragstart.prevent
      >
        <img
          :src="bannerPreviewUrl"
          alt="Tournament banner preview"
          class="banner-preview"
          draggable="false"
          decoding="async"
          :style="imageStyle"
          @load="onImageLoad"
        />

        <span class="banner-drag-label" aria-hidden="true">
          <drag-icon />
          Drag to reposition
        </span>
      </div>
      <div v-else class="banner-empty">No banner</div>

      <ui-file-drop v-model="selectedBanner" accept="image/*" />
    </div>

    <template #footer>
      <ui-button size="sm" variant="secondary" :disabled="isBannerUpdating" @click="cancel">
        Cancel
      </ui-button>
      <ui-button
        size="sm"
        variant="secondary"
        :disabled="isBannerUpdating || !tournament?.banner"
        @click="removeBanner"
      >
        Remove
      </ui-button>
      <ui-button size="sm" :disabled="isBannerUpdating || !canSave" @click="saveBanner">
        <loading-icon v-if="isBannerUpdating" />
        Save
      </ui-button>
    </template>
  </ui-modal>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { useQueryClient } from '@tanstack/vue-query'

import LoadingIcon from '@/icons/LoadingIcon.vue'
import UiModal from '@/components/ui/UiModal.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiFileDrop from '@/components/ui/UiFileDrop.vue'

import DragIcon from '@/icons/DragIcon.vue'

import { toObjectPosition } from '@/lib/imagePosition'
import { useNotification } from '@/composables/useNotification'
import { useBannerPosition } from '../../../composables/useBannerPosition'
import {
  getGetTournamentQueryKey,
  useDeleteTournamentBanner,
  useGetTournament,
  useUpdateTournamentBanner,
} from '@/api/tournaments/tournaments'

const props = defineProps<{ tournamentId: number }>()

const isOpen = defineModel({ default: false })

const selectedBanner = ref<File[]>([])
const selectedBannerUrl = ref('')
const isDragging = ref(false)

const queryClient = useQueryClient()
const { showNotification } = useNotification()
const { data: tournament } = useGetTournament(props.tournamentId)
const { mutate: updateBanner, isPending: isUpdatingBanner } = useUpdateTournamentBanner()
const { mutate: removeTournamentBanner, isPending: isRemovingBanner } = useDeleteTournamentBanner()

const { position, save: savePosition, clear: clearPosition } = useBannerPosition(props.tournamentId)

const draft = ref({ ...position.value })

const positionChanged = computed(
  () => draft.value.x !== position.value.x || draft.value.y !== position.value.y,
)
const canSave = computed(() => selectedBanner.value.length > 0 || positionChanged.value)

const isBannerUpdating = computed(() => isUpdatingBanner.value || isRemovingBanner.value)
const bannerPreviewUrl = computed(() => selectedBannerUrl.value || tournament.value?.banner || '')

const frameRef = ref<HTMLElement | null>(null)
const frameSize = ref({ w: 0, h: 0 })
const naturalSize = ref({ w: 0, h: 0 })

const onImageLoad = (e: Event) => {
  const img = e.target as HTMLImageElement
  naturalSize.value = { w: img.naturalWidth, h: img.naturalHeight }
}

watch(bannerPreviewUrl, () => {
  naturalSize.value = { w: 0, h: 0 }
})

let resizeObserver: ResizeObserver | null = null
watch(frameRef, (el) => {
  resizeObserver?.disconnect()
  resizeObserver = null
  if (!el) return
  frameSize.value = { w: el.clientWidth, h: el.clientHeight }
  resizeObserver = new ResizeObserver(() => {
    frameSize.value = { w: el.clientWidth, h: el.clientHeight }
  })
  resizeObserver.observe(el)
})

const layout = computed(() => {
  const { w: fw, h: fh } = frameSize.value
  const { w: nw, h: nh } = naturalSize.value

  if (!fw || !fh || !nw || !nh) return null

  const scale = Math.max(fw / nw, fh / nh)
  const width = nw * scale
  const height = nh * scale

  return { width, height, overflowX: width - fw, overflowY: height - fh }
})

const imageStyle = computed(() => {
  const l = layout.value

  if (!l) return { objectPosition: toObjectPosition(draft.value) }

  const tx = (-l.overflowX * draft.value.x) / 100
  const ty = (-l.overflowY * draft.value.y) / 100

  return {
    width: `${l.width}px`,
    height: `${l.height}px`,
    transform: `translate3d(${tx}px, ${ty}px, 0)`,
  }
})

const PREVIEW_MAX_SIZE = 1600
let previewToken = 0

const createPreviewUrl = async (file: File): Promise<string> => {
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

const revokePreviewUrl = () => {
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

const refreshTournament = () =>
  queryClient.invalidateQueries({ queryKey: getGetTournamentQueryKey(props.tournamentId) })

const resetBannerState = () => {
  previewToken++
  selectedBanner.value = []
  draft.value = { ...position.value }
  isDragging.value = false
  revokePreviewUrl()
}

const cancel = () => {
  resetBannerState()
  isOpen.value = false
}

const onBannerPreviewPointerDown = (event: PointerEvent) => {
  const target = event.currentTarget as HTMLElement | null
  const l = layout.value
  if (!target || !l) return

  target.setPointerCapture(event.pointerId)
  isDragging.value = true

  const clamp = (n: number) => Math.min(100, Math.max(0, n))

  const startX = event.clientX
  const startY = event.clientY
  const startPosition = { ...draft.value }

  let rafId = 0
  let lastEvent: PointerEvent | null = null

  const computeDelta = (e: PointerEvent) => {
    const dx = e.clientX - startX
    const dy = e.clientY - startY
    draft.value = {
      x: l.overflowX > 1 ? clamp(startPosition.x - (dx / l.overflowX) * 100) : startPosition.x,
      y: l.overflowY > 1 ? clamp(startPosition.y - (dy / l.overflowY) * 100) : startPosition.y,
    }
  }

  const applyDelta = (e: PointerEvent) => {
    lastEvent = e
    if (rafId) return
    rafId = requestAnimationFrame(() => {
      rafId = 0
      if (lastEvent) computeDelta(lastEvent)
    })
  }

  const handleUp = (e: PointerEvent) => {
    cancelAnimationFrame(rafId)
    rafId = 0
    computeDelta(e)
    isDragging.value = false
    target.removeEventListener('pointermove', applyDelta)
    target.removeEventListener('pointerup', handleUp)
    target.removeEventListener('pointercancel', handleUp)
  }

  target.addEventListener('pointermove', applyDelta)
  target.addEventListener('pointerup', handleUp)
  target.addEventListener('pointercancel', handleUp)
}

const saveBanner = () => {
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

const removeBanner = () => {
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
  resizeObserver?.disconnect()
})
</script>

<style scoped>
.banner-modal-body {
  display: grid;
  gap: 0.75rem;
}

.banner-preview {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  max-width: none;
  object-fit: cover;
  user-select: none;
  -webkit-user-drag: none;
  pointer-events: none;
  will-change: transform;
}

.banner-empty {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--color-gray-500);
  font-size: 0.85rem;
}

.banner-preview-frame,
.banner-empty {
  width: 100%;
  max-width: 480px;
  aspect-ratio: 16 / 5;
  border-radius: 0.6rem;
  border: 1px solid var(--line-soft);
}

.banner-preview-frame {
  position: relative;
  overflow: hidden;
  cursor: all-scroll;
  user-select: none;
  -webkit-user-select: none;
  touch-action: none;
}

.banner-drag-label {
  position: absolute;
  left: 50%;
  bottom: 0.6rem;
  transform: translateX(-50%);
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.3rem 0.7rem;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  font-size: 0.78rem;
  white-space: nowrap;
  pointer-events: none;
  transition: opacity 0.2s ease;
}

.banner-preview-frame.is-dragging .banner-drag-label {
  opacity: 0;
}
</style>
