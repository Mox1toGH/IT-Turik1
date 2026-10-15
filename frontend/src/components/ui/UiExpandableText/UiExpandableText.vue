<template>
  <div class="ui-expandable">
    <div
      ref="bodyRef"
      class="ui-expandable__body"
      :class="{ 'ui-expandable__body--clamped': !expanded }"
    >
      <slot>{{ text }}</slot>
    </div>
    <button
      v-if="isOverflowing"
      type="button"
      class="ui-expandable__toggle"
      :aria-expanded="expanded"
      @click="expanded = !expanded"
    >
      {{ expanded ? collapseLabel : expandLabel }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

interface Props {
  text?: string
  lines?: number
  expandLabel?: string
  collapseLabel?: string
}

const props = withDefaults(defineProps<Props>(), {
  text: undefined,
  lines: 3,
  expandLabel: 'Show more',
  collapseLabel: 'Show less',
})

const bodyRef = ref<HTMLElement | null>(null)
const expanded = ref(false)
const isOverflowing = ref(false)
let observer: ResizeObserver | null = null

const clampLines = computed(() => Math.max(1, Math.round(props.lines)))

const checkOverflow = () => {
  const el = bodyRef.value
  if (!el) {
    isOverflowing.value = false
    return
  }
  // While expanded the full content is visible, so scrollHeight ~= clientHeight.
  // Measuring now would wrongly report "no overflow", hide the toggle and
  // immediately collapse again — making "Show more" look broken.
  if (expanded.value) return
  isOverflowing.value = el.scrollHeight > el.clientHeight + 1
}

const scheduleCheck = () => {
  void nextTick(checkOverflow)
}

onMounted(() => {
  scheduleCheck()
  if (typeof ResizeObserver !== 'undefined' && bodyRef.value) {
    observer = new ResizeObserver(checkOverflow)
    observer.observe(bodyRef.value)
  }
  // Webfonts can change line breaks after mount; re-check once they settle.
  const fonts = (document as Document & { fonts?: { ready: Promise<unknown> } }).fonts
  if (fonts) {
    void fonts.ready.then(checkOverflow)
  }
})

watch([() => props.text, () => props.lines], () => {
  // New content must be measured in clamped state; otherwise a previous
  // expanded=true would skip the overflow check and leave a stale toggle.
  expanded.value = false
  scheduleCheck()
})
// Slot content has no reactive prop to watch — ResizeObserver above already
// re-checks when slotted content changes the body size.

onBeforeUnmount(() => {
  observer?.disconnect()
  observer = null
})

defineExpose({ expanded, isOverflowing, checkOverflow })
</script>

<style scoped>
.ui-expandable {
  min-width: 0;
}

.ui-expandable__body {
  min-width: 0;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

.ui-expandable__body--clamped {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: v-bind(clampLines);
  line-clamp: v-bind(clampLines);
  overflow: hidden;
}

.ui-expandable__toggle {
  margin-top: 0.35rem;
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--primary);
  font: inherit;
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  font-weight: 700;
  cursor: pointer;
}

.ui-expandable__toggle:hover {
  text-decoration: underline;
  text-underline-offset: 2px;
}

.ui-expandable__toggle:focus-visible {
  outline: 2px solid var(--ring);
  outline-offset: 2px;
  border-radius: 4px;
}
</style>
