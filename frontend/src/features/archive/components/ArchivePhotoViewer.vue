<template>
  <div
    class="photo-viewer-layer"
    role="presentation"
    @click.self="emit('close')"
    @touchstart.passive="onTouchStart"
    @touchend.passive="onTouchEnd"
  >
    <article
      class="photo-viewer"
      role="dialog"
      aria-modal="true"
      aria-label="Archive photo record"
      :class="{ 'viewer-glitch': viewerGlitch }"
    >
      <div class="viewer-toolbar">
        <button ref="closeButton" type="button" @click.stop="emit('close')">← CLOSE FILE</button
        ><span>{{ currentPhoto.filename }}</span>
      </div>
      <div class="viewer-main">
        <button
          type="button"
          class="viewer-nav"
          aria-label="Previous photo"
          @click.stop="movePhoto(-1)"
        >
          ‹
        </button>
        <figure class="viewer-image-frame">
          <img
            :key="currentPhoto.id"
            :src="currentPhoto.src"
            :alt="currentPhoto.filename"
            decoding="async"
            fetchpriority="high"
          />
        </figure>
        <button type="button" class="viewer-nav" aria-label="Next photo" @click.stop="movePhoto(1)">
          ›
        </button>
      </div>
      <div class="dossier">
        <div>
          <span>TITLE</span><b>{{ currentPhoto.title }}</b>
        </div>
        <div>
          <span>DESCRIPTION</span>
          <p>{{ currentPhoto.description }}</p>
        </div>
      </div>
      <div class="viewer-foot">
        <span>{{ currentIndex + 1 }} / {{ photos.length }}</span
        ><span>← → NAVIGATE · ESC CLOSE</span>
      </div>
    </article>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import type { ArchivePhotoFile } from '../data/foundArchive'

interface Props {
  photo: ArchivePhotoFile
  photos: ArchivePhotoFile[]
  index: number
}

interface Emits {
  close: []
  navigate: [file: ArchivePhotoFile, index: number]
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const currentIndex = ref(props.index)
const currentPhoto = computed(() => props.photos[currentIndex.value] ?? props.photo)
const viewerGlitch = ref(false)
const closeButton = ref<HTMLButtonElement | null>(null)

let glitchTimer: ReturnType<typeof setTimeout> | undefined
let touchStartX = 0
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

function preloadNeighbors() {
  if (!props.photos.length) return

  for (const offset of [-1, 1]) {
    const neighbor =
      props.photos[(currentIndex.value + offset + props.photos.length) % props.photos.length]

    if (neighbor) {
      const image = new Image()
      image.src = neighbor.src
    }
  }
}

function movePhoto(offset: number) {
  if (!props.photos.length) return

  currentIndex.value = (currentIndex.value + offset + props.photos.length) % props.photos.length
  const nextPhoto = currentPhoto.value

  emit('navigate', nextPhoto, currentIndex.value)
  preloadNeighbors()
}

function onTouchStart(event: TouchEvent) {
  touchStartX = event.changedTouches[0]?.clientX ?? 0
}

function onTouchEnd(event: TouchEvent) {
  const delta = (event.changedTouches[0]?.clientX ?? touchStartX) - touchStartX
  if (Math.abs(delta) > 55) movePhoto(delta < 0 ? 1 : -1)
}

function onKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') emit('close')
  else if (event.key === 'ArrowLeft') movePhoto(-1)
  else if (event.key === 'ArrowRight') movePhoto(1)
}

onMounted(() => {
  closeButton.value?.focus()
  preloadNeighbors()

  if (!reducedMotion && Math.random() < 0.12) {
    viewerGlitch.value = true
    glitchTimer = setTimeout(() => (viewerGlitch.value = false), 180)
  }
  window.addEventListener('keydown', onKeydown)
})
onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
  if (glitchTimer) clearTimeout(glitchTimer)
})
</script>

<style scoped>
.photo-viewer-layer {
  position: fixed;
  z-index: 100;
  inset: 0;
  display: grid;
  place-items: center;
  overflow: auto;
  padding: 12px;
  background: rgba(1, 5, 2, 0.91);
  backdrop-filter: blur(3px);
}
.photo-viewer {
  box-sizing: border-box;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto auto;
  width: min(1240px, 100%);
  height: 100%;
  max-height: 100%;
  overflow: auto;
  border: 1px solid rgba(144, 174, 101, 0.55);
  background: #0c160e;
  color: #cad8a6;
  box-shadow: 0 0 34px rgba(104, 145, 65, 0.14);
}
.viewer-toolbar,
.viewer-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 9px 12px;
  border-bottom: 1px solid rgba(144, 174, 101, 0.22);
  color: #9cad7d;
  font-size: 11px;
  letter-spacing: 0.06em;
}
.viewer-toolbar > span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.viewer-toolbar button {
  border: 1px solid rgba(154, 179, 111, 0.35);
  background: #111e13;
  color: #d5e1bb;
  padding: 7px 10px;
  font: inherit;
  font-size: 11px;
  letter-spacing: 0.06em;
  cursor: pointer;
}
.viewer-main {
  display: grid;
  grid-template-columns: 38px minmax(0, 1fr) 38px;
  align-items: center;
  gap: 8px;
  min-height: 0;
  overflow: hidden;
  padding: 12px;
}
.viewer-image-frame {
  position: relative;
  display: grid;
  place-items: center;
  overflow: hidden;
  width: 100%;
  height: 100%;
  min-width: 0;
  min-height: 0;
  margin: 0;
  background: #050a06;
}
.viewer-image-frame img {
  display: block;
  width: auto;
  height: auto;
  min-width: 0;
  min-height: 0;
  max-width: 100%;
  max-height: 100%;
  object-fit: contain !important;
}
.dossier {
  display: grid;
  grid-template-columns: minmax(0, 0.8fr) minmax(0, 1.2fr);
  gap: 8px 20px;
  padding: 9px 14px;
  border-top: 1px solid rgba(144, 174, 101, 0.22);
  background: rgba(28, 39, 24, 0.45);
}
.dossier > div {
  display: grid;
  align-content: start;
  gap: 4px;
  min-width: 0;
}
.dossier span {
  color: #91a575;
  font-size: 10px;
  letter-spacing: 0.14em;
}
.dossier b,
.dossier p {
  margin: 0;
  color: #cbd8aa;
  font-size: 13px;
  line-height: 1.35;
}
.viewer-nav {
  width: 34px;
  height: 48px;
  border: 1px solid rgba(147, 174, 102, 0.34);
  background: #101b11;
  color: #bbd391;
  font-size: 27px;
  cursor: pointer;
}
@keyframes archive-photo-glitch {
  25% {
    transform: translateX(5px);
  }
  70% {
    transform: translateX(-4px);
  }
}
@media (max-width: 760px) {
  .photo-viewer-layer {
    padding: 7px;
  }
  .viewer-main {
    grid-template-columns: 28px minmax(0, 1fr) 28px;
    gap: 4px;
    min-height: 30vh;
    padding: 7px 4px;
  }
  .viewer-image-frame {
    min-height: 30vh;
  }
  .viewer-nav {
    width: 27px;
    height: 42px;
  }
  .dossier {
    grid-template-columns: 1fr;
    gap: 6px;
    padding: 8px 10px;
  }
  .dossier b,
  .dossier p {
    font-size: 12px;
  }
}
@media (max-height: 620px) {
  .photo-viewer-layer {
    padding: 4px;
  }
  .viewer-toolbar,
  .viewer-foot {
    padding-top: 5px;
    padding-bottom: 5px;
  }
  .viewer-main {
    padding: 5px;
  }
  .dossier {
    padding-top: 5px;
    padding-bottom: 5px;
  }
}
@media (max-width: 760px) and (max-height: 620px) {
  .viewer-main {
    min-height: 0;
    padding: 3px;
  }
  .viewer-image-frame {
    min-height: 0;
  }
}
@media (prefers-reduced-motion: reduce) {
  .viewer-glitch {
    animation: none !important;
  }
  .viewer-fade-enter-active,
  .viewer-fade-leave-active {
    transition-duration: 0.15s;
  }
}
</style>
