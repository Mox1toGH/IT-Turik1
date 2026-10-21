<template>
  <div
    v-if="previewUrl"
    ref="frameRef"
    class="banner-preview-frame"
    :class="{ 'is-dragging': isDragging }"
    @pointerdown.prevent="onBannerPreviewPointerDown"
    @dragstart.prevent
  >
    <img
      :src="previewUrl"
      alt="Tournament banner preview"
      class="banner-preview"
      draggable="false"
      decoding="async"
      :style="imageStyle"
      @load="onImageLoad"
    />

    <span class="banner-drag-label" aria-hidden="true">
      <Move :size="14" />
      Drag to reposition
    </span>
  </div>
  <div v-else class="banner-empty">No banner</div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { Move } from 'lucide-vue-next'
import { toObjectPosition } from '@/lib/imagePosition'
import type { BannerPosition } from '../../../composables/useBannerUpload'

const props = defineProps<{
  previewUrl: string
}>()

const draft = defineModel<BannerPosition>('draft', { required: true })

const isDragging = ref<boolean>(false)
const frameRef = ref<HTMLElement | null>(null)
const frameSize = ref({ w: 0, h: 0 })
const naturalSize = ref({ w: 0, h: 0 })

const onImageLoad = (e: Event): void => {
  const img = e.target as HTMLImageElement
  naturalSize.value = { w: img.naturalWidth, h: img.naturalHeight }
}

watch(
  () => props.previewUrl,
  () => {
    naturalSize.value = { w: 0, h: 0 }
  },
)

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

const onBannerPreviewPointerDown = (event: PointerEvent): void => {
  const target = event.currentTarget as HTMLElement | null
  const l = layout.value
  if (!target || !l) return

  target.setPointerCapture(event.pointerId)
  isDragging.value = true

  const clamp = (n: number): number => Math.min(100, Math.max(0, n))

  const startX = event.clientX
  const startY = event.clientY
  const startPosition = { ...draft.value }

  let rafId = 0
  let lastEvent: PointerEvent | null = null

  const computeDelta = (e: PointerEvent): void => {
    const dx = e.clientX - startX
    const dy = e.clientY - startY
    draft.value = {
      x: l.overflowX > 1 ? clamp(startPosition.x - (dx / l.overflowX) * 100) : startPosition.x,
      y: l.overflowY > 1 ? clamp(startPosition.y - (dy / l.overflowY) * 100) : startPosition.y,
    }
  }

  const applyDelta = (e: PointerEvent): void => {
    lastEvent = e
    if (rafId) return
    rafId = requestAnimationFrame(() => {
      rafId = 0
      if (lastEvent) computeDelta(lastEvent)
    })
  }

  const handleUp = (e: PointerEvent): void => {
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

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
})
</script>

<style scoped>
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
  color: var(--muted-foreground);
  font-size: 0.85rem;
}

.banner-preview-frame,
.banner-empty {
  width: 100%;
  max-width: 480px;
  aspect-ratio: 16 / 5;
  border-radius: var(--radius);
  border: 1px solid var(--border);
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
  background: var(--scrim);
  color: var(--on-image);
  font-size: 0.78rem;
  white-space: nowrap;
  pointer-events: none;
  transition: opacity 0.2s ease;
}

.banner-preview-frame.is-dragging .banner-drag-label {
  opacity: 0;
}
</style>
