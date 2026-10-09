<template>
  <ui-card class="section-block">
    <template #header>
      <div class="section-head">
        <h2>Summary</h2>
        <p class="section-note">Archive overview</p>
      </div>
    </template>
    <div class="stats-grid">
      <ui-card class="stat-card">
        <p class="stat-label">Rounds</p>
        <p class="stat-value">{{ roundsCount }}</p>
      </ui-card>
      <ui-card class="stat-card">
        <p class="stat-label">Submissions</p>
        <p class="stat-value">{{ submissionsCount }}</p>
      </ui-card>
      <ui-card class="stat-card">
        <p class="stat-label">Winner</p>
        <p class="stat-value">{{ winnerName }}</p>
      </ui-card>
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard.vue'

defineProps<{
  roundsCount: number
  submissionsCount: number
  winnerName: string
}>()
</script>

<style scoped>
.section-block {
  display: grid;
  gap: 0.6rem;
}

.section-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.8rem;
  flex-wrap: wrap;
}

.section-block h2 {
  margin: 0;
}

.section-note {
  margin: 0;
  color: var(--muted-foreground);
  font-size: 0.88rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.8rem;
}

.stat-card {
  background: linear-gradient(
    135deg,
    color-mix(in srgb, var(--muted) 90%, transparent),
    color-mix(in srgb, var(--background) 85%, transparent)
  ) !important;
  border: 1px solid color-mix(in srgb, var(--line-soft) 70%, transparent);
}

.stat-label,
.stat-value {
  margin: 0;
}

.stat-label {
  color: var(--muted-foreground);
}

.stat-value {
  font-size: clamp(1.25rem, 2vw, 1.55rem);
  font-weight: 700;
}

@media (max-width: 980px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .section-note {
    width: 100%;
  }
}
</style>
