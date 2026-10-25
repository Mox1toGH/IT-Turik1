<template>
  <ui-card class="stats-section" title="statistics">
    <template #header>
      <h2>Statistics</h2>
    </template>

    <ui-query-block :query="adminQuery">
      <template #error>
        <div class="error-state">
          <p>{{ errorMessage }}</p>
        </div>
      </template>

      <ui-query-field>
        <template #skeleton>
          <div class="stats-grid">
            <ui-skeleton v-for="n in 6" :key="n" variant="rect" height="84px" />
          </div>
        </template>
        <div class="stats-grid">
          <ui-card v-for="item in statsCards" :key="item.label" class="stat-card">
            <p class="stat-label">{{ item.label }}</p>
            <p class="stat-value">{{ item.value }}</p>
          </ui-card>
        </div>
      </ui-query-field>
    </ui-query-block>
  </ui-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import UiCard from '@/components/ui/UiCard'
import { UiQueryBlock, UiQueryField } from '@/components/query'
import UiSkeleton from '@/components/ui/UiSkeleton'
import { useGetAdminStats } from '@/api/stats/stats'

const adminQuery = useGetAdminStats()
const { data: adminStats } = adminQuery

const errorMessage = computed(
  () => adminQuery.error.value?.message ?? 'Failed to load statistics. Please try again.',
)

const roleBreakdown = computed(() => {
  const breakdown = adminStats.value?.users_by_role ?? []
  if (breakdown.length === 0) return 'No data'
  return breakdown.map((item) => `${item.role}: ${item.count}`).join(', ')
})

const statsCards = computed(() => [
  { label: 'Total users', value: String(adminStats.value?.total_users ?? 0) },
  { label: 'Total teams', value: String(adminStats.value?.total_teams ?? 0) },
  { label: 'Total tournaments', value: String(adminStats.value?.total_tournaments ?? 0) },
  {
    label: 'New registrations (7d / 30d)',
    value: `${adminStats.value?.new_registrations_last_7_days ?? 0} / ${
      adminStats.value?.new_registrations_last_30_days ?? 0
    }`,
  },
  { label: 'Active tournaments', value: String(adminStats.value?.active_tournaments ?? 0) },
  { label: 'Role breakdown', value: roleBreakdown.value },
])
</script>

<style scoped>
.stats-section h2 {
  margin-top: 0;
  font-family: var(--font-display);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.75rem;
}

.stat-card {
  gap: 0.35rem;
}

.stat-label {
  margin: 0;
  color: var(--muted-foreground);
  font-size: 0.82rem;
}

.stat-value {
  margin: 0;
  font-size: 1.08rem;
  font-weight: 700;
  line-height: 1.35;
  overflow-wrap: anywhere;
}

.error-state {
  min-height: 110px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: var(--muted-foreground);
}

@media (max-width: 980px) {
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
