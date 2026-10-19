<template>
  <ui-section title="Summary" description="Archive overview">
    <div class="stats-grid">
      <ui-card variant="stat" class="stat-card">
        <p class="stat-label">Rounds</p>
        <p class="stat-value">{{ roundsCount }}</p>
      </ui-card>
      <ui-card variant="stat" class="stat-card">
        <p class="stat-label">Submissions</p>
        <p class="stat-value">{{ submissionsCount }}</p>
      </ui-card>
      <ui-card variant="stat" class="stat-card">
        <p class="stat-label">Winner</p>
        <p class="stat-value">{{ winnerName }}</p>
      </ui-card>
    </div>
  </ui-section>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard'
import UiSection from '@/components/ui/UiSection'

defineProps<{
  roundsCount: number
  submissionsCount: number
  winnerName: string
}>()
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 0.8rem;
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
</style>
