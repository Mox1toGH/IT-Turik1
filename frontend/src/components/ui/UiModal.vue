<template>
  <DialogRoot :open="isOpen" @update:open="handleOpenChange">
    <DialogPortal>
      <Transition name="modal-overlay">
        <DialogOverlay
          v-if="isOpen"
          ref="modalBackdrop"
          class="modal-backdrop"
          data-testid="modal-backdrop"
        />
      </Transition>

      <Transition name="modal">
        <DialogContent
          v-if="isOpen"
          class="modal-content"
          :style="{ width: `min(100%, ${maxWidth})`, zIndex: 51 + level * 2 }"
          @pointer-down-outside="handlePointerDownOutside"
        >
          <ui-card :scrollable="props.scrollable">
            <div class="modal-header">
              <DialogTitle v-if="$slots.title" as-child>
                <span class="modal-title"><slot name="title" /></span>
              </DialogTitle>
              <VisuallyHidden v-else as-child>
                <DialogTitle>Dialog</DialogTitle>
              </VisuallyHidden>

              <VisuallyHidden as-child>
                <DialogDescription>Dialog content</DialogDescription>
              </VisuallyHidden>

              <DialogClose as-child>
                <ui-button
                  style="margin-left: auto"
                  variant="secondary"
                  size="sm"
                  aria-label="Close"
                >
                  <CrossIcon />
                </ui-button>
              </DialogClose>
            </div>

            <slot />

            <template #footer>
              <div v-if="$slots.footer" class="modal-footer">
                <slot name="footer" />
              </div>
            </template>
          </ui-card>
        </DialogContent>
      </Transition>
    </DialogPortal>
  </DialogRoot>
</template>

<script setup lang="ts">
import CrossIcon from '@/icons/CrossIcon.vue'
import UiButton from './UiButton.vue'
import UiCard from './UiCard.vue'
import {
  DialogRoot,
  DialogPortal,
  DialogOverlay,
  DialogContent,
  DialogTitle,
  DialogDescription,
  DialogClose,
  VisuallyHidden,
} from 'reka-ui'
import { ref } from 'vue'

interface Props {
  defaultOpen?: boolean
  maxWidth?: string
  closeOnBackdrop?: boolean
  scrollable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  defaultOpen: false,
  maxWidth: '520px',
  closeOnBackdrop: true,
})

const emit = defineEmits(['close'])
const isOpen = defineModel<boolean>({ default: false })

if (props.defaultOpen) {
  isOpen.value = true
}

const level = ref(1)

function getOpenedCount() {
  return Number(document.documentElement.getAttribute('modals-opened') ?? 1)
}

function incrementOpenedCount() {
  level.value += 1
  document.documentElement.setAttribute('modals-opened', level.value.toString())
}

function decrementOpenedCount() {
  if (level.value != 0) level.value -= 1
  document.documentElement.setAttribute('modals-opened', level.value.toString())
}

function open() {
  isOpen.value = true
  incrementOpenedCount()
}

function close() {
  isOpen.value = false
  decrementOpenedCount()
  emit('close')
}

function handleOpenChange(value: boolean) {
  isOpen.value = value

  if (value) {
    level.value = getOpenedCount()
    incrementOpenedCount()
  } else {
    decrementOpenedCount()
    emit('close')
  }
}

function handlePointerDownOutside(e: Event) {
  if (!props.closeOnBackdrop) {
    e.preventDefault()
  }
  decrementOpenedCount()
}

defineExpose({ open, close, isOpen })
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: #00000073;
  backdrop-filter: blur(3px);
  z-index: 50;
}

.modal-content {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 51;
  max-height: calc(100vh - 2rem);
  max-width: calc(100vw - 2rem);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-title {
  display: contents;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.6rem;
}

.modal-enter-active,
.modal-leave-active {
  transition:
    opacity 0.15s ease,
    transform 0.15s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
  transform: translate(-50%, calc(-50% + 4px));
}

.modal-overlay-enter-active,
.modal-overlay-leave-active {
  transition: opacity 0.15s ease;
}

.modal-overlay-enter-from,
.modal-overlay-leave-to {
  opacity: 0;
}
</style>
