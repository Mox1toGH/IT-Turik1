<template>
  <section class="page-shell">
    <ui-card :is-error="isError">
      <template #header>
        <div class="tournaments-header">
          <h1 class="tournaments-title">Tournaments list</h1>
          <ui-button
            v-if="user?.role === 'admin'"
            size="sm"
            asLink
            to="/tournaments/create"
            class="create-new-btn"
            >Create new</ui-button
          >
        </div>
      </template>

      <template #error>
        <div style="display: flex; height: 300px; justify-content: center; align-items: center">
          <p>Error while fetching tournaments (code: {{ error?.code }})</p>
        </div>
      </template>

      <div>
        <div class="filters-wrapper">
          <div class="search-wrapper">
            <ui-input
              v-model="searchInput"
              class="search-input"
              placeholder="Search tournament by name"
              @keydown.enter="applySearch"
            />

            <ui-button v-if="searchInput.length >= 2" @click="applySearch"
              ><arrow-right
            /></ui-button>
          </div>

          <div class="filters">
            <ui-select
              v-model="statusFilter"
              :options="statusOptions"
              placeholder="All statuses"
              :multiple="true"
              align-to="right"
              min-width="180px"
              @update:model-value="onStatusChange"
            >
              <template #trigger="{ selectedLabel }">
                <ui-button variant="ghost" size="sm" style="justify-self: end">{{
                  selectedLabel
                }}</ui-button>
              </template>
            </ui-select>
          </div>
        </div>

        <ui-skeleton-loader :loading="isLoading || isFetching">
          <template #skeleton>
            <div class="tournaments-grid">
              <ui-card v-for="i in pageSize" :key="i" class="tournament-card">
                <template #header>
                  <ui-skeleton variant="rect" width="70%" height="24px" />
                </template>

                <ui-skeleton variant="rect" class="tournaments-description" height="48px" />

                <div class="tournaments-meta">
                  <div class="tournaments-date">
                    <ui-skeleton variant="rect" width="60px" />
                    <ui-skeleton variant="rect" width="130px" />
                  </div>

                  <ui-skeleton variant="rect" width="120px" height="28px" />
                </div>

                <ui-skeleton variant="rect" width="100%" height="36px" />
              </ui-card>
            </div>
          </template>

          <div>
            <template v-if="pageItems.length">
              <div class="tournaments-grid">
                <ui-card
                  v-for="tournament in pageItems"
                  :key="tournament.id"
                  class="tournament-card"
                >
                  <template #header>
                    <h3 class="tounament-title" :title="tournament.name">
                      {{ truncateText(tournament.name, 80) }}
                    </h3>
                  </template>

                  <div class="tournament-info">
                    <p class="tournaments-description" :title="tournament.description">
                      {{ truncateText(tournament.description, 200) }}
                    </p>

                    <div class="tournaments-meta">
                      <div class="tournaments-date">
                        <p>Start date:</p>

                        <p>
                          {{ formatDate(tournament.start_date) }}
                        </p>
                      </div>

                      <ui-badge :variant="statusBadgeVariant(tournament.status)">
                        {{ tournament.status }}
                      </ui-badge>
                    </div>
                  </div>

                  <template #footer>
                    <ui-button
                      size="sm"
                      asLink
                      :to="`/tournaments/${tournament.id}`"
                      variant="secondary"
                      class="tournaments-details-btn"
                    >
                      View details
                    </ui-button>
                  </template>
                </ui-card>
              </div>
            </template>

            <ui-card v-if="!isError && pageItems.length === 0" class="empty-card"
              ><p class="empty-error">No tournaments found</p></ui-card
            >

            <div v-if="totalPages > 1" class="pagination">
              <ui-button size="sm" :disabled="currentPage === 1" @click="goToPage(currentPage - 1)">
                Prev
              </ui-button>

              <ui-button
                v-for="page in visiblePages"
                :key="`${page}`"
                size="sm"
                class="pagination-btn"
                :disabled="page === '...'"
                :variant="page === currentPage ? 'default' : 'secondary'"
                @click="typeof page === 'number' && goToPage(page)"
              >
                {{ page }}
              </ui-button>

              <ui-button
                size="sm"
                :disabled="currentPage === totalPages"
                @click="goToPage(currentPage + 1)"
              >
                Next
              </ui-button>
            </div>
          </div>
        </ui-skeleton-loader>
      </div>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiSelect from '@/components/ui/UiSelect.vue'
import ArrowRight from '@/icons/ArrowRight.vue'
import { parseApiError } from '@/api/errors'
import { truncateText } from '@/lib/utils'
import { useProfile } from '@/api/queries/accounts'
import { useTournaments } from '@/api/queries/tournaments'
import { formatDate } from '@/lib/date'
import type { GetTournamentsArgs } from '@/api/services/tournaments/types'
import type { TournamentStatus } from '@/api/dbTypes'

const statusOptions = computed(() => {
  const base = [
    { label: 'Draft', value: 'draft' },
    { label: 'Registration', value: 'registration' },
    { label: 'Running', value: 'running' },
    { label: 'Finished', value: 'finished' },
  ]

  return user.value?.role === 'admin' ? base : base.filter((option) => option.value !== 'draft')
})

const pageSize = 12

const currentPage = ref(1)
const searchInput = ref('')
const searchQuery = ref('')
const statusFilter = ref<NonNullable<GetTournamentsArgs['status']>>([])

const { data: user } = useProfile()
const {
  data,
  isLoading,
  isFetching,
  error: tournamentsError,
  isError,
} = useTournaments(
  { page: currentPage, searchQuery, pageSize, status: statusFilter },
  {
    staleTime: 1000 * 60 * 5,
  },
)
const error = computed(() => parseApiError(tournamentsError.value))

const pageItems = computed(() => data.value?.data ?? [])
const totalPages = computed(() => Math.ceil((data.value?.total ?? 0) / pageSize))
const statusBadgeVariant = (status: TournamentStatus) => {
  if (status === 'draft') return 'gray'
  if (status === 'finished') return 'gray'
  if (status === 'running') return 'green'
  if (status === 'registration') return 'orange'

  return 'gray'
}

const visiblePages = computed(() => {
  const total = totalPages.value
  const current = currentPage.value

  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i + 1)
  }

  if (current <= 4) {
    return [1, 2, 3, 4, 5, '...', total]
  }

  if (current >= total - 3) {
    return [1, '...', total - 4, total - 3, total - 2, total - 1, total]
  }

  return [1, '...', current - 1, current, current + 1, '...', total]
})

const goToPage = (page: number) => {
  if (page < 1 || page > totalPages.value) {
    return
  }
  currentPage.value = page
}

const applySearch = () => {
  currentPage.value = 1
  searchQuery.value = searchInput.value
}

const onStatusChange = () => {
  currentPage.value = 1
}
</script>

<style scoped>
.tournaments-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filters-wrapper {
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filters {
  display: flex;
  gap: 0.4rem;
  justify-content: end;
}

.search-wrapper {
  display: flex;
  justify-content: space-between;
  gap: 0.3rem;
}

.search-input {
  flex: 1;
}

.tournaments-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.tounament-title {
  word-break: break-word;
}

.tournament-info {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.tournaments-description {
  flex: 1;
  margin-bottom: 12px;
  line-height: 1.5;
  word-break: break-word;
}

.tournament-card {
  background: var(--muted) !important;
}

.tournaments-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  color: var(--muted-foreground);
}

.tournaments-date {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tournaments-date p {
  margin: 0;
}

.tournaments-details-btn {
  width: 100%;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 24px;
}

.pagination-btn {
  width: 40px;
  min-width: 40px;
  height: 40px;
  padding: 0;
}

@media (max-width: 1024px) {
  .tournaments-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .tournaments-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .tournaments-meta {
    flex-direction: column;
    align-items: flex-start;
  }

  .pagination {
    gap: 6px;
    margin-top: 20px;
  }
}

@media (max-width: 480px) {
  .pagination {
    flex-wrap: nowrap;
    overflow-x: auto;
    padding-bottom: 4px;
  }

  .tournaments-header {
    flex-direction: column;
    align-items: start;
  }

  .create-new-btn {
    width: 100%;
  }
}
</style>
