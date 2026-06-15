<template>
  <div class="popover-root" ref="rootRef" :style="{ display: inline ? 'inline-flex' : 'flex' }">
    <slot name="trigger" :is-open="isOpen" :toggle="toggle" :open="open" :close="close" />

    <Transition name="popover">
      <div
        v-if="isOpen"
        class="popover-content"
        :class="[`align-${align}`, `side-${side}`]"
        :style="{ width, minWidth, maxWidth }"
        @click.stop
      >
        <div class="popover-header" v-if="header">
          {{ header }}
        </div>

        <slot :close="close" />
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

interface Props {
  align?: 'start' | 'center' | 'end'
  side?: 'bottom' | 'top'
  width?: string
  minWidth?: string
  maxWidth?: string
  inline?: boolean
  header?: string
  closeOnEsc?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  align: 'start',
  side: 'bottom',
  inline: true,
  closeOnEsc: true,
})

const emit = defineEmits<{
  open: []
  close: []
}>()

const isOpen = ref(false)
const rootRef = ref<HTMLElement | null>(null)

const open = () => {
  isOpen.value = true
  emit('open')
}
const close = () => {
  isOpen.value = false
  emit('close')
}
const toggle = () => (isOpen.value ? close() : open())

const onClickOutside = (e: MouseEvent) => {
  if (!rootRef.value?.contains(e.target as Node)) close()
}

const onKeydown = (e: KeyboardEvent) => {
  if (props.closeOnEsc && e.key === 'Escape') close()
}

onMounted(() => {
  document.addEventListener('mousedown', onClickOutside)
  document.addEventListener('keydown', onKeydown)
})
onUnmounted(() => {
  document.removeEventListener('mousedown', onClickOutside)
  document.removeEventListener('keydown', onKeydown)
})

defineExpose({ open, close, toggle, isOpen })
</script>

<style scoped>
.popover-root {
  position: relative;
}

.popover-header {
  font-size: 0.9rem;
  color: var(--muted-foreground);
  padding-bottom: 0.3rem;
  margin-bottom: 0.3rem;
  border-bottom: 1px solid var(--border);
}

.popover-content {
  position: absolute;
  z-index: 200;
  background: var(--popover, var(--background));
  color: var(--popover-foreground, var(--foreground));
  border: 1px solid color-mix(in srgb, var(--border) 60%, transparent);
  border-radius: 12px;
  padding: 0.6rem;
  box-shadow:
    0 4px 6px -1px rgb(0 0 0 / 0.07),
    0 12px 24px -4px rgb(0 0 0 / 0.1);
  outline: none;
}

.popover-content.side-bottom {
  top: calc(100% + 6px);
}
.popover-content.side-top {
  bottom: calc(100% + 6px);
}

.popover-content.align-start {
  left: 0;
}
.popover-content.align-center {
  left: 50%;
  transform: translateX(-50%);
}
.popover-content.align-end {
  right: 0;
}

.popover-enter-active,
.popover-leave-active {
  transition:
    opacity 0.13s ease,
    transform 0.13s ease;
}
.popover-content.side-bottom.popover-enter-active,
.popover-content.side-bottom.popover-leave-active {
  transform-origin: top left;
}
.popover-content.side-bottom.align-center.popover-enter-active,
.popover-content.side-bottom.align-center.popover-leave-active {
  transform-origin: top center;
}
.popover-content.side-bottom.align-end.popover-enter-active,
.popover-content.side-bottom.align-end.popover-leave-active {
  transform-origin: top right;
}
.popover-content.side-top.popover-enter-active,
.popover-content.side-top.popover-leave-active {
  transform-origin: bottom left;
}
.popover-enter-from,
.popover-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(-4px);
}
.popover-content.side-top.popover-enter-from,
.popover-content.side-top.popover-leave-to {
  transform: scale(0.95) translateY(4px);
}
</style>
