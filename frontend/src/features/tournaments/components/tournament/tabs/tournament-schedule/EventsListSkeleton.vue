<template>
  <div class="events-list">
    <ui-card v-for="i in 5" :key="`event-skeleton-${i}`" class="event-card">
      <div class="event-content">
        <div class="event-left-side">
          <ui-skeleton variant="rounded" width="50px" height="50px" />
          <div class="event-info">
            <ui-skeleton variant="rect" width="140px" />
            <ui-skeleton variant="rect" width="220px" />
          </div>
        </div>
        <div class="event-right-side">
          <ui-skeleton variant="rect" width="150px" />
        </div>
      </div>
    </ui-card>
  </div>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard'
import UiSkeleton from '@/components/ui/UiSkeleton'
</script>

<style scoped>
.events-list {
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
  padding-left: 20px;
  margin-left: 10px;
  border-left: 1px solid var(--border);
}
.event-card {
  position: relative;
}
.event-card::before {
  content: '';
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  left: -30px;
  width: 15px;
  height: 15px;
  border-radius: 50%;
  background: var(--primary);
}
.event-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}
.event-left-side,
.event-right-side {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.event-info {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  min-width: 0;
}
@media (max-width: 600px) {
  .event-content,
  .event-left-side {
    align-items: flex-start;
  }
  .event-content {
    flex-direction: column;
  }
}
</style>
