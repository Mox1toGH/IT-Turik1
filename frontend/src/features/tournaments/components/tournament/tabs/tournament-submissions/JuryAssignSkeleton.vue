<template>
  <div class="submissions-table">
    <div v-for="i in 2" :key="`skeleton-${i}`" class="table-row">
      <div class="team-cell">
        <div class="team-avatar">
          <ui-skeleton variant="rounded" width="40px" height="40px" />
        </div>
        <div class="skeleton-lines">
          <ui-skeleton variant="rect" width="100px" />
          <ui-skeleton variant="rect" width="140px" />
        </div>
      </div>
      <ui-skeleton variant="rect" width="100px" />
      <ui-skeleton variant="rect" width="100px" />
      <ui-skeleton variant="rect" width="100px" />
    </div>
  </div>
</template>

<script setup lang="ts">
import UiSkeleton from '@/components/ui/UiSkeleton'
</script>

<style scoped>
.submissions-table {
  display: grid;
}
.table-row {
  display: grid;
  grid-template-columns: 2.5fr 2fr 2.3fr 2fr;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-top: 1px solid var(--border);
}
.table-row:first-child {
  border-top: 0;
}
.team-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.team-avatar {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: var(--primary-foreground);
  background: var(--primary);
}
.skeleton-lines {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 8px;
}
@media (max-width: 820px) {
  .table-row {
    grid-template-columns: 1fr;
    row-gap: 0.75rem;
  }
}
</style>
