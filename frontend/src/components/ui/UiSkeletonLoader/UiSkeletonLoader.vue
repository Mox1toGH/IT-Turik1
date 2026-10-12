<template>
  <Transition name="skeleton-fade" mode="out-in">
    <div :key="loading ? 'skeleton' : 'content'" :style="containerStyle">
      <slot v-if="loading" name="skeleton" />
      <slot v-else />
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  loading: boolean
  minWidth?: string
}

const props = withDefaults(defineProps<Props>(), {
  loading: true,
})

const containerStyle = computed(() => ({
  minWidth: props.minWidth,
}))
</script>

<style scoped>
.skeleton-fade-enter-active {
  transition: opacity 0.2s ease;
}

.skeleton-fade-leave-active {
  transition: opacity 0.1s ease;
}

.skeleton-fade-enter-from {
  opacity: 0;
}

.skeleton-fade-leave-to {
  opacity: 0;
}
</style>
