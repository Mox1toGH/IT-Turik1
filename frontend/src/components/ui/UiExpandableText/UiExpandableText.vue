<template>
  <div class="ui-expandable">
    <div
      ref="bodyRef"
      class="ui-expandable__body"
      :class="{ 'ui-expandable__body--clamped': !expanded }"
      :style="!expanded ? { maxHeight: `${collapsedHeight}px` } : undefined"
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
import { computed, nextTick, onBeforeUnmount, onMounted, ref, useSlots, watch } from 'vue'

interface Props {
  text?: string
  lines?: number
  expandLabel?: string
  collapseLabel?: string
  lineHeight?: number
}

const props = withDefaults(defineProps<Props>(), {
  text: undefined,
  lines: 3,
  expandLabel: 'Show more',
  collapseLabel: 'Show less',
  lineHeight: 24,
})

const slots = useSlots()
const bodyRef = ref<HTMLElement | null>(null)
const expanded = ref(false)
const isOverflowing = ref(false)
let observer: ResizeObserver | null = null

// Max-height clamp (instead of line-clamp) so rich/tiptap HTML also clamps.
const collapsedHeight = computed(() => props.lines * props.lineHeight)

const checkOverflow = () => {
  const el = bodyRef.value
  if (!el) {
    isOverflowing.value = false
    return
  }
  isOverflowing.value = el.scrollHeight > collapsedHeight.value + 1
  // If content shrank back to fit, collapse again so no toggle lingers.
  if (!isOverflowing.value) expanded.value = false
}

onMounted(() => {
  void nextTick(checkOverflow)
  if (typeof ResizeObserver !== 'undefined' && bodyRef.value) {
    observer = new ResizeObserver(checkOverflow)
    observer.observe(bodyRef.value)
  }
})

watch([() => props.text, () => props.lines, () => slots.default], () => {
  void nextTick(checkOverflow)
})

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
  overflow-wrap: anywhere;
}

.ui-expandable__body--clamped {
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
