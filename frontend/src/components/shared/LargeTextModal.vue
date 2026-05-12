<template>
  <div
    class="modal-trigger"
    v-bind="$attrs"
    :class="{ 'modal-trigger--active': text.length > Number(maxLength) }"
  >
    <slot name="trigger" :toggleOpen="toggleOpen" />

    <external-link-icon
      v-if="text.length > Number(maxLength)"
      class="modal-trigger__icon text-muted"
      width="15px"
      height="15px"
    />
  </div>

  <ui-modal v-if="text.length > Number(maxLength)" v-model="isOpen" scrollable>
    <template #title>
      <h3>{{ title }}</h3>
    </template>

    <p class="text-muted large-text">
      {{ props.text }}
    </p>
  </ui-modal>
</template>

<script setup lang="ts">
import UiModal from '@/components/ui/UiModal.vue'
import ExternalLinkIcon from '@/icons/ExternalLinkIcon.vue'
import { ref } from 'vue'

interface Props {
  title: string
  text: string
  maxLength: number | string
}

const props = defineProps<Props>()
const isOpen = ref(false)

const toggleOpen = () => {
  isOpen.value = !isOpen.value
}
</script>

<style scoped>
.modal-trigger {
  position: relative;
  padding-right: 22px;
}

.modal-trigger__icon {
  position: absolute;
  top: 0;
  right: 0;
}

.modal-trigger--active:hover {
  cursor: pointer;
  background: color-mix(in srgb, var(--foreground) 8%, transparent);
}

.large-text {
  word-break: break-all;
}
</style>
