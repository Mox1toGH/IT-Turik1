<template>
  <section class="tournaments-page page-shell">
    <tournaments-hero
      :total="data?.total ?? 0"
      :shown="pageItems.length"
      :loading="isLoading"
      :is-admin="isAdmin"
    />

    <div class="tournaments-rule" aria-hidden="true"></div>

    <section class="tournaments-section">
      <div v-if="isError" class="error-state">
        <p>Error while fetching tournaments</p>
      </div>

      <ui-card v-else variant="panel" class="tournaments-panel">
        <template #header>
          <div class="section-head">
            <div>
              <p class="section-eyebrow">Discover</p>
              <h2 class="text-3xl">Active tournaments</h2>
              <p class="section-subtitle text-base">
                Filter competitions by name or registration status.
              </p>
            </div>

            <div class="section-meta">
              <span class="count-pill text-base">{{ pageItems.length }} shown</span>
            </div>
          </div>
        </template>

        <tournament-filters
          v-model:status="statusFilter"
          :status-options="statusOptions"
          @search="onSearch"
        />

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
            <div v-if="pageItems.length" class="tournaments-grid">
              <tournament-card
                v-for="tournament in pageItems"
                :key="tournament.id"
                :tournament="tournament"
              />
            </div>

            <ui-card v-else class="empty-card">
              <div class="empty-row">
                <div class="empty-icon" aria-hidden="true">+</div>
                <div class="empty-copy">
                  <h3 class="text-lg">No tournaments found</h3>
                  <p class="text-base">Try changing the search text or status filters.</p>
                </div>
              </div>
            </ui-card>

            <ui-pagination
              v-if="(data?.total ?? 0) > pageSize"
              v-model="currentPage"
              :total-items="data?.total ?? 0"
              :page-size="pageSize"
            />
          </div>
        </ui-skeleton-loader>
      </ui-card>
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import UiPagination from '@/components/ui/UiPagination.vue'
import TournamentsHero from '../components/tournament-list/TournamentsHero.vue'
import TournamentFilters from '../components/tournament-list/TournamentFilters.vue'
import TournamentCard from '../components/tournament-list/TournamentCard.vue'
import { useGetUserProfile } from '@/api/accounts/accounts'
import { useListTournaments } from '@/api/tournaments/tournaments'
import type { ListTournamentsParams, TournamentStatus } from '@/api/backendAPINinja.schemas'

const currentPage = ref(1)
const pageSize = 12
const searchQuery = ref('')
const statusFilter = ref<TournamentStatus[]>([])

const { data: user } = useGetUserProfile()
const isAdmin = computed(() => user.value?.role === 'admin')

const statusOptions = computed(() => {
  const base = [
    { label: 'Draft', value: 'draft' },
    { label: 'Registration', value: 'registration' },
    { label: 'Running', value: 'running' },
    { label: 'Finished', value: 'finished' },
  ]

  return isAdmin.value ? base : base.filter((option) => option.value !== 'draft')
})

const params = computed<ListTournamentsParams>(() => ({
  page: currentPage.value,
  searchQuery: searchQuery.value,
  page_size: pageSize,
  status: statusFilter.value.join(','),
}))

const { data, isLoading, isFetching, isError } = useListTournaments(params, {
  query: { staleTime: 1000 * 60 * 5 },
})

const pageItems = computed(() => data.value?.data ?? [])

const onSearch = (query: string) => {
  currentPage.value = 1
  searchQuery.value = query
}

watch(statusFilter, () => {
  currentPage.value = 1
})
</script>

<style scoped>
.tournaments-page {
  gap: 1.4rem;
}

.tournaments-rule {
  height: 1px;
  margin: 0.7rem 0 0.9rem;
  background: var(--line-soft);
}

.tournaments-section,
.tournaments-panel {
  min-width: 0;
}

.section-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.section-head h2 {
  margin: 0.3rem 0 0.45rem;
  font-family: var(--font-display);
  font-weight: 800;
}

.section-head .section-subtitle {
  margin: 0;
}

.section-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 1rem;
}

.count-pill {
  display: inline-flex;
  align-items: center;
  min-height: 38px;
  padding: 0.35rem 0.8rem;
  border: 1px solid var(--line-soft);
  border-radius: 999px;
  color: var(--muted-foreground);
  white-space: nowrap;
}

.tournaments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 0.9rem;
}

.tournaments-description {
  flex: 1;
  margin: 0;
}

.tournaments-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.tournaments-date {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* empty state */
.empty-card {
  background: transparent;
  border: 0;
  padding: 0;
}

.empty-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  min-height: 96px;
  padding: 1.35rem;
  border: 1px dashed var(--line-soft);
  border-radius: 16px;
  background: var(--background);
}

.empty-icon {
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: color-mix(in srgb, var(--primary) 22%, transparent);
  color: var(--primary);
  font-size: var(--text-2xl);
  font-weight: 800;
}

.empty-copy {
  min-width: 0;
}

.empty-copy h3,
.empty-copy p {
  margin: 0;
}

.empty-copy h3 {
  color: var(--foreground);
  font-weight: 800;
}

.empty-copy p {
  margin-top: 0.25rem;
  color: var(--muted-foreground);
}

.error-state {
  display: flex;
  min-height: 136px;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--line-soft);
  border-radius: 16px;
  background: var(--card);
}

@media (max-width: 760px) {
  .tournaments-page {
    padding: 1rem 1rem 2rem;
  }

  .section-head,
  .empty-row {
    align-items: stretch;
    flex-direction: column;
  }

  .section-meta {
    justify-content: flex-start;
    align-items: flex-start;
  }

  .tournaments-meta {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
