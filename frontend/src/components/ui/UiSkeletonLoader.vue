<template>
  <Transition name="skeleton-fade" mode="out-in">
    <div v-if="loading">
      <slot name="skeleton" />
    </div>

    <div v-else>
      <slot />
    </div>
  </Transition>
</template>

<script setup lang="ts">
interface Props {
  loading: boolean
  minWidth?: string
}

withDefaults(defineProps<Props>(), {
  loading: true,
})
</script>

<style scoped>
.skeleton-fade-enter-active {
  transition:
    opacity 0.3s ease,
    filter 0.3s ease;
}

.skeleton-fade-leave-active {
  transition: opacity 0.15s ease;
}

.skeleton-fade-enter-from {
  opacity: 0;
  filter: blur(2px);
}

.skeleton-fade-enter-to {
  opacity: 1;
  filter: blur(0);
}

.skeleton-fade-leave-to {
  opacity: 0;
}
</style>
