<template>
  <div
    :class="[
      'horizontal-scroll',
      {
        'can-scroll-left': canScrollLeft,
        'can-scroll-right': canScrollRight,
      },
    ]"
  >
    <button
      v-if="canScrollLeft"
      type="button"
      class="scroll-control scroll-control-left"
      :aria-label="props.leftLabel"
      @click="scrollByDirection(-1)"
    >
      <span aria-hidden="true">&lt;</span>
    </button>

    <div
      ref="viewportRef"
      :class="['horizontal-scroll-viewport', props.contentClass]"
      :role="props.role"
      @scroll="scheduleScrollStateUpdate"
    >
      <slot />
    </div>

    <button
      v-if="canScrollRight"
      type="button"
      class="scroll-control scroll-control-right"
      :aria-label="props.rightLabel"
      @click="scrollByDirection(1)"
    >
      <span aria-hidden="true">&gt;</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'

type Props = {
  role?: string
  contentClass?: string
  leftLabel?: string
  rightLabel?: string
}

const props = withDefaults(defineProps<Props>(), {
  role: undefined,
  contentClass: '',
  leftLabel: 'Scroll left',
  rightLabel: 'Scroll right',
})

const viewportRef = ref<HTMLElement | null>(null)
const canScrollLeft = ref(false)
const canScrollRight = ref(false)

let resizeObserver: ResizeObserver | null = null
let frameId = 0

function updateScrollState() {
  const viewport = viewportRef.value
  if (!viewport) return

  const maxScrollLeft = viewport.scrollWidth - viewport.clientWidth
  canScrollLeft.value = viewport.scrollLeft > 1
  canScrollRight.value = viewport.scrollLeft < maxScrollLeft - 1
}

function scheduleScrollStateUpdate() {
  if (frameId) window.cancelAnimationFrame(frameId)
  frameId = window.requestAnimationFrame(() => {
    frameId = 0
    updateScrollState()
  })
}

function scrollByDirection(direction: -1 | 1) {
  const viewport = viewportRef.value
  if (!viewport) return

  viewport.scrollBy({
    left: direction * Math.max(viewport.clientWidth * 0.75, 160),
    behavior: 'smooth',
  })
}

onMounted(() => {
  void nextTick(() => {
    updateScrollState()
  })

  resizeObserver = new ResizeObserver(scheduleScrollStateUpdate)
  if (viewportRef.value) {
    resizeObserver.observe(viewportRef.value)
  }
  window.addEventListener('resize', scheduleScrollStateUpdate)
})

onBeforeUnmount(() => {
  if (frameId) window.cancelAnimationFrame(frameId)
  resizeObserver?.disconnect()
  window.removeEventListener('resize', scheduleScrollStateUpdate)
})
</script>

<style scoped>
.horizontal-scroll {
  position: relative;
  min-width: 0;
}

.horizontal-scroll::before,
.horizontal-scroll::after {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  z-index: 1;
  width: 2.75rem;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.18s ease;
}

.horizontal-scroll::before {
  left: 0;
  background: linear-gradient(90deg, var(--card), transparent);
}

.horizontal-scroll::after {
  right: 0;
  background: linear-gradient(270deg, var(--card), transparent);
}

.horizontal-scroll.can-scroll-left::before,
.horizontal-scroll.can-scroll-right::after {
  opacity: 1;
}

.horizontal-scroll-viewport {
  display: flex;
  gap: 0.25rem;
  overflow-x: auto;
  padding: 0.35rem;
  scroll-behavior: smooth;
  scrollbar-width: none;
}

.horizontal-scroll-viewport::-webkit-scrollbar {
  display: none;
}

.scroll-control {
  position: absolute;
  top: 50%;
  z-index: 2;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.75rem;
  height: 1.75rem;
  border: 1px solid var(--line-soft);
  border-radius: 999px;
  background: var(--card);
  color: var(--foreground);
  box-shadow: 0 8px 18px color-mix(in srgb, var(--foreground) 14%, transparent);
  cursor: pointer;
  transform: translateY(-50%);
}

.scroll-control:hover {
  color: var(--primary);
  border-color: color-mix(in srgb, var(--primary) 45%, var(--line-soft));
}

.scroll-control:focus-visible {
  outline: none;
  box-shadow:
    0 0 0 2px var(--ring),
    0 8px 18px color-mix(in srgb, var(--foreground) 14%, transparent);
}

.scroll-control span {
  display: block;
  margin-top: -0.1rem;
  font-size: 1.45rem;
  line-height: 1;
}

.scroll-control-left {
  left: 0.25rem;
}

.scroll-control-right {
  right: 0.25rem;
}
</style>
