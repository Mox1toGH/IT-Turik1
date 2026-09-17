<template>
  <ui-modal v-model="isOpen" maxWidth="min(96vw, 1200px)">
    <template #title>Image Preview</template>
    <div class="image-preview-wrap">
      <img v-if="url" :src="url" class="image-preview-full" alt="Preview" />
    </div>
  </ui-modal>
</template>

<script setup lang="ts">
import UiModal from '@/components/ui/UiModal.vue'

defineProps<{ url?: string }>()

const isOpen = defineModel<boolean>({ default: false })
</script>

<style scoped>
.image-preview-wrap {
  display: grid;
  place-items: center;
  min-height: min(70vh, 720px);
}
.image-preview-full {
  max-width: 100%;
  max-height: 70vh;
  width: auto;
  height: auto;
  object-fit: contain;
  border-radius: 10px;
}
</style>
