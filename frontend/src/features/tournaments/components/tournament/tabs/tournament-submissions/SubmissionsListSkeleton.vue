<template>
  <div class="submissions-list">
    <div v-for="i in 3" :key="`submission-skeleton-${i}`" class="submission-row">
      <div class="submission-header">
        <div class="left-side">
          <div class="left-side-icon"><FileCheck :size="20" /></div>
          <div class="round-info">
            <p class="text-muted">Round</p>
            <ui-skeleton width="140px" />
          </div>
        </div>
        <div class="right-side">
          <div class="round-info">
            <p class="text-muted">submitted on</p>
            <ui-skeleton width="120px" />
          </div>
          <div class="round-info">
            <p class="text-muted">status</p>
            <ui-skeleton width="120px" />
          </div>
        </div>
      </div>
      <div class="skeleton-body">
        <ui-skeleton width="120px" />
        <ui-skeleton width="180px" />
        <ui-skeleton width="140px" />
      </div>
      <div class="submission-footer">
        <div class="submission-links">
          <ui-skeleton width="80px" />
          <ui-skeleton width="80px" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { FileCheck } from 'lucide-vue-next'
import UiSkeleton from '@/components/ui/UiSkeleton'
</script>

<style scoped>
.submissions-list {
  display: flex;
  flex-direction: column;
}
.submission-row {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  padding: 1rem 0;
  border-top: 1px solid var(--border);
}
.submission-row:first-child {
  border-top: 0;
  padding-top: 0;
}
.submission-header {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--border);
}
.left-side-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 50px;
  height: 50px;
  padding: 0.7rem;
  background: var(--primary-soft);
  color: var(--primary);
  border-radius: 50%;
}
.round-info,
.right-side,
.left-side {
  display: flex;
  gap: 1rem;
  align-items: center;
}
.round-info {
  flex-direction: column;
  gap: 0.25rem;
  align-items: flex-start;
}
.round-info p {
  margin: 0;
}
.skeleton-body {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.submission-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
}
.submission-links {
  display: flex;
  align-items: center;
  gap: 1rem;
}
</style>
