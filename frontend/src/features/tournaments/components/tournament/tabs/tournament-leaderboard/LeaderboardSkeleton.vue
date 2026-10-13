<template>
  <div class="table-skeleton">
    <ui-skeleton variant="rect" height="40px" />
    <ui-skeleton v-for="i in 5" :key="i" variant="rect" height="52px" />
  </div>
</template>

<script setup lang="ts">
import UiSkeleton from '@/components/ui/UiSkeleton'
</script>

<style scoped>
.table-skeleton {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
</style>
