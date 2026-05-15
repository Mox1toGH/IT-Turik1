<template>
  <section class="page-shell">
    <ui-card>
      <template #header>
        <div class="head">
          <div>
            <p class="section-eyebrow">Tournaments</p>
            <h1 class="section-title">
              {{ isOwnView ? 'My tournament history' : `${displayUserName} tournament history` }}
            </h1>
          </div>
          <ui-button variant="secondary" @click="goBack">Back</ui-button>
        </div>
      </template>

      <ui-skeleton-loader :loading="isLoading">
        <template #skeleton>
          <div class="history-list">
            <ui-card v-for="i in 4" :key="`skeleton-${i}`" class="history-card">
              <ui-skeleton variant="rect" width="60%" height="24px" />
              <ui-skeleton variant="rect" width="100%" height="18px" />
              <ui-skeleton variant="rect" width="45%" height="18px" />
              <ui-skeleton variant="rect" width="100%" height="34px" />
            </ui-card>
          </div>
        </template>

        <p v-if="isError" class="text-muted">
          Failed to load tournament history ({{ historyError?.code ?? 'unknown' }}).
        </p>

        <p v-else-if="!historyItems.length" class="text-muted">
          No tournament history yet.
        </p>

        <div v-else class="history-list">
          <ui-card v-for="item in historyItems" :key="`${item.tournament_id}-${item.team.id}`" class="history-card">
            <template #header>
              <div class="history-head">
                <h3 class="history-title">{{ item.tournament_name }}</h3>
                <ui-badge :variant="statusVariant(item.tournament_status)">
                  {{ item.tournament_status }}
                </ui-badge>
              </div>
            </template>

            <div class="history-grid">
              <p><strong>Dates:</strong> {{ formatDateRange(item.start_date, item.end_date) }}</p>
              <p><strong>Team:</strong> {{ item.team.name }}</p>
              <p><strong>Final place:</strong> {{ item.final_rank ? `#${item.final_rank}` : '-' }}</p>
              <p><strong>Final score:</strong> {{ formatScore(item.final_score) }}</p>
            </div>

            <template #footer>
              <ui-button
                as-link
                :to="`/tournaments/archive/${item.tournament_id}`"
                variant="secondary"
                size="sm"
                class="open-btn"
              >
                Open archive
              </ui-button>
            </template>
          </ui-card>
        </div>
      </ui-skeleton-loader>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import { useGetUser, useGetUserProfile, useListUserTournamentHistory } from '@/api/accounts/accounts'

const route = useRoute()
const router = useRouter()
const { data: viewer } = useGetUserProfile()

const routeUserId = computed(() => Number(route.params.id || 0))
const isOwnView = computed(() => !route.params.id)
const targetUserId = computed(() => (isOwnView.value ? Number(viewer.value?.id || 0) : routeUserId.value))

const { data: viewedUser } = useGetUser(routeUserId, {
  query: { enabled: computed(() => !isOwnView.value && routeUserId.value > 0) },
})
const {
  data: history,
  isLoading,
  isError,
  error: historyError,
} = useListUserTournamentHistory(targetUserId, {
  query: { enabled: computed(() => targetUserId.value > 0) },
})

const historyItems = computed(() => history.value ?? [])
const displayUserName = computed(() => viewedUser.value?.full_name || viewedUser.value?.username || 'User')

const goBack = () => {
  if (isOwnView.value) {
    router.push('/profile')
    return
  }
  router.push(`/users/${routeUserId.value}`)
}

const formatDate = (value?: string | null) => {
  if (!value) return 'N/A'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'N/A'
  return new Intl.DateTimeFormat(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(date)
}

const formatDateRange = (start?: string | null, end?: string | null) => {
  return `${formatDate(start)} - ${formatDate(end)}`
}

const formatScore = (score?: string | null) => {
  if (!score) return '-'
  const normalized = Number(score)
  if (Number.isNaN(normalized)) return '-'
  return Number.isInteger(normalized) ? String(normalized) : normalized.toFixed(2)
}

const statusVariant = (status?: string) => {
  if (status === 'running') return 'green'
  if (status === 'registration') return 'orange'
  return 'gray'
}
</script>

<style scoped>
.head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.history-list {
  display: grid;
  gap: 10px;
}

.history-card {
  background: var(--muted);
  color: var(--muted-foreground);
}

.history-head {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  align-items: center;
}

.history-title {
  margin: 0;
  word-break: break-word;
}

.history-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.history-grid p {
  margin: 0;
}

.open-btn {
  width: 100%;
}

@media (max-width: 760px) {
  .head {
    flex-direction: column;
    align-items: flex-start;
  }

  .history-grid {
    grid-template-columns: 1fr;
  }
}
</style>
