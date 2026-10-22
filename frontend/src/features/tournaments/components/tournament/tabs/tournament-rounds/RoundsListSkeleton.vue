<template>
  <div class="rounds-list">
    <ui-card v-for="i in 3" :key="`round-skeleton-${i}`" class="round-card">
      <template #header>
        <div class="round-header">
          <ui-skeleton variant="rect" width="180px" height="24px" />
          <ui-skeleton variant="rect" width="80px" height="24px" />
        </div>
      </template>
      <div class="skeleton-lines">
        <ui-skeleton variant="rect" width="220px" />
        <ui-skeleton variant="rect" width="220px" />
      </div>
      <div class="round-actions">
        <ui-skeleton variant="rect" width="110px" height="36px" />
      </div>
    </ui-card>
  </div>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard'
import UiSkeleton from '@/components/ui/UiSkeleton'
</script>

<style scoped>
.rounds-list {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.8rem;
}
.round-card {
  min-width: 0;
}
.round-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.8rem;
}
.skeleton-lines {
  display: grid;
  gap: 0.3rem;
}
.round-actions {
  display: flex;
  justify-content: end;
  align-items: center;
  gap: 8px;
  margin-top: 1rem;
}
@media (max-width: 900px) {
  .rounds-list {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
@media (max-width: 600px) {
  .rounds-list {
    grid-template-columns: 1fr;
  }
}
</style>
