<template>
  <UiHoverCard v-if="tooltip && isTruncated" :open-delay="300">
    <template #trigger>
      <span ref="textRef" :class="truncateClass" :title="plainText"><slot>{{ text }}</slot></span>
    </template>
    <span class="ui-truncate__full">{{ fullText }}<slot name="tooltip" /></span>
  </UiHoverCard>
  <span v-else ref="textRef" :class="truncateClass"><slot>{{ text }}</slot></span>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, useSlots, watch } from 'vue'
import UiHoverCard from '../UiHoverCard'

interface Props {
  text?: string
  lines?: number
  tooltip?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  text: undefined,
  lines: 1,
  tooltip: true,
})

const slots = useSlots()
const textRef = ref<HTMLElement | null>(null)
const isTruncated = ref(false)
let observer: ResizeObserver | null = null

const plainText = computed(() => props.text ?? '')
const fullText = computed(() => props.text ?? '')

const truncateClass = computed(() => [
  'ui-truncate',
  props.lines <= 1 ? 'ui-truncate--single' : 'ui-truncate--multi',
])

const checkTruncation = () => {
  const el = textRef.value
  if (!el || !props.tooltip) {
    isTruncated.value = false
    return
  }
  // Works for both single-line (scrollWidth) and clamped (scrollHeight) text.
  isTruncated.value = el.scrollWidth > el.clientWidth + 1 || el.scrollHeight > el.clientHeight + 1
}

onMounted(() => {
  checkTruncation()
  if (typeof ResizeObserver !== 'undefined' && textRef.value) {
    observer = new ResizeObserver(checkTruncation)
    observer.observe(textRef.value)
  }
})

watch([() => props.text, () => props.lines, () => slots.default], checkTruncation, {
  flush: 'post',
})

onBeforeUnmount(() => {
  observer?.disconnect()
  observer = null
})

defineExpose({ isTruncated, checkTruncation })
</script>

<style scoped>
.ui-truncate {
  display: block;
  min-width: 0;
  overflow: hidden;
}

.ui-truncate--single {
  white-space: nowrap;
  text-overflow: ellipsis;
}

.ui-truncate--multi {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  line-clamp: v-bind(lines);
  -webkit-line-clamp: v-bind(lines);
}

.ui-truncate__full {
  overflow-wrap: anywhere;
}
</style>
