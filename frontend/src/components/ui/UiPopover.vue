<template>
  <PopoverRoot :open="isOpen" @update:open="handleOpenChange">
    <PopoverTrigger as-child :style="{ display: inline ? 'inline-flex' : 'flex' }">
      <slot name="trigger" :is-open="isOpen" :toggle="toggle" :open="open" :close="close" />
    </PopoverTrigger>

    <PopoverPortal>
      <Transition name="popover">
        <PopoverContent
          v-if="isOpen"
          class="popover-content"
          :style="{ width, minWidth, maxWidth }"
          :side="side"
          :align="align"
          :side-offset="sideOffset"
          @escape-key-down="handleEscapeKeyDown"
        >
          <div v-if="header" class="popover-header">
            {{ header }}
          </div>

          <slot :close="close" />
        </PopoverContent>
      </Transition>
    </PopoverPortal>
  </PopoverRoot>
</template>

<script setup lang="ts">
import { PopoverRoot, PopoverTrigger, PopoverPortal, PopoverContent } from 'reka-ui'

interface Props {
  align?: 'start' | 'center' | 'end'
  side?: 'bottom' | 'top'
  sideOffset?: number
  width?: string
  minWidth?: string
  maxWidth?: string
  inline?: boolean
  header?: string
  closeOnEsc?: boolean
  defaultOpen?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  align: 'start',
  side: 'bottom',
  sideOffset: 6,
  inline: true,
  closeOnEsc: true,
  defaultOpen: false,
})

const emit = defineEmits<{
  open: []
  close: []
}>()

const isOpen = defineModel<boolean>({ default: false })

if (props.defaultOpen) {
  isOpen.value = true
}

function open() {
  isOpen.value = true
  emit('open')
}

function close() {
  isOpen.value = false
  emit('close')
}

function toggle() {
  isOpen.value ? close() : open()
}

function handleOpenChange(value: boolean) {
  if (value) open()
  else close()
}

function handleEscapeKeyDown(e: Event) {
  if (!props.closeOnEsc) e.preventDefault()
}

defineExpose({ open, close, toggle, isOpen })
</script>

<style scoped>
:deep(.popover-header) {
  font-size: 0.9rem;
  color: var(--muted-foreground);
  padding-bottom: 0.3rem;
  margin-bottom: 0.3rem;
  border-bottom: 1px solid var(--border);
}

:deep(.popover-content) {
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

:deep(.popover-enter-active),
:deep(.popover-leave-active) {
  transition:
    opacity 0.13s ease,
    transform 0.13s ease;
  transform-origin: var(--reka-popper-transform-origin);
}

:deep(.popover-enter-from),
:deep(.popover-leave-to) {
  opacity: 0;
  transform: scale(0.95);
}
</style>
