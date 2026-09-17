<template>
  <section class="tournaments-page page-shell">
    <header class="tournaments-hero">
      <div class="tournaments-hero-copy">
        <div class="breadcrumb-label">
          <span>Workspace</span>
          <span aria-hidden="true">/</span>
          <span>Tournaments</span>
        </div>

        <h1 class="text-6xl">Tournaments list</h1>
        <p class="section-subtitle text-xl">
          Browse active competitions, track registration, and open tournament workspaces.
        </p>
      </div>

      <div class="hero-actions">
        <ui-skeleton-loader :loading="isLoading">
          <template #skeleton>
            <ui-skeleton variant="rect" width="148px" height="64px" />
          </template>

          <ui-card variant="stat" class="tournaments-stat-card">
            <strong class="text-2xl">{{ data?.total ?? 0 }}</strong>
            <span class="text-sm">Total results</span>
          </ui-card>
        </ui-skeleton-loader>

        <ui-card variant="stat" class="tournaments-stat-card">
          <strong class="text-2xl">{{ pageItems.length }}</strong>
          <span class="text-sm">Showing now</span>
        </ui-card>

        <ui-button asLink to="/tournaments/archive" variant="default" size="lg">Archive</ui-button>
        <ui-button v-if="user?.role === 'admin'" asLink to="/tournaments/create" size="lg">
          <span class="create-plus text-2xl" aria-hidden="true">+</span>
          Create tournament
        </ui-button>
      </div>
    </header>

    <div class="tournaments-rule" aria-hidden="true"></div>

    <section class="tournaments-section">
      <div v-if="isError" class="error-state">
        <p>Error while fetching tournaments (code: {{ tournamentsError?.code }})</p>
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

        <div class="filters-wrapper">
          <div class="search-wrapper">
            <ui-input
              v-model="searchInput"
              class="search-input"
              placeholder="Search tournament by name"
              @keydown.enter="applySearch"
            />

            <ui-button
              v-if="searchInput.length >= 2"
              class="search-button"
              aria-label="Search tournaments"
              @click="applySearch"
            >
              <arrow-right />
            </ui-button>
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
                  <div class="tournament-top">
                    <img
                      v-if="tournament.banner"
                      class="tournament-banner"
                      :src="tournament.banner"
                      :alt="`${tournament.name} banner`"
                    />
                    <h3 class="tounament-title" :title="tournament.name">
                      {{ truncateText(tournament.name, 80) }}
                    </h3>

                    <p class="tournaments-description" :title="tournament.description">
                      {{ truncateText(tournament.description, 200) }}
                    </p>
                  </div>

                  <div class="tournament-info">
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
                      variant="default"
                    >
                      View details
                    </ui-button>
                  </template>
                </ui-card>
              </div>
            </template>

            <ui-card v-if="!isError && pageItems.length === 0" class="empty-card">
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
import { computed, ref, type Ref } from 'vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiSelect from '@/components/ui/UiSelect.vue'
import UiPagination from '@/components/ui/UiPagination.vue'
import ArrowRight from '@/icons/ArrowRight.vue'
import { truncateText } from '@/lib/utils'
import { formatDate } from '@/lib/date'
import { useGetUserProfile } from '@/api/accounts/accounts'
import type { ListTournamentsParams, StatusD67Enum } from '@/api/.ts.schemas'
import { useListTournaments } from '@/api/tournaments/tournaments'

const statusOptions = computed(() => {
  const base = [
    { label: 'Draft', value: 'draft' },
    { label: 'Registration', value: 'registration' },
    { label: 'Running', value: 'running' },
    { label: 'Finished', value: 'finished' },
  ]

  return user.value?.role === 'admin' ? base : base.filter((option) => option.value !== 'draft')
})

const currentPage = ref(1)
const pageSize = 12
const searchInput = ref('')
const searchQuery = ref('')
const statusFilter = ref<NonNullable<StatusD67Enum[]>>([])

const { data: user } = useGetUserProfile()
const params = computed(() => ({
  page: currentPage.value,
  searchQuery: searchQuery.value,
  page_size: pageSize,
  status: statusFilter.value.join(','),
})) as unknown as Ref<ListTournamentsParams>
const {
  data,
  isLoading,
  isFetching,
  error: tournamentsError,
  isError,
} = useListTournaments(params, {
  query: { staleTime: 1000 * 60 * 5 },
})

const pageItems = computed(() => data.value?.data ?? [])
const statusBadgeVariant = (status?: StatusD67Enum) => {
  if (status === 'draft') return 'gray'
  if (status === 'finished') return 'gray'
  if (status === 'running') return 'green'
  if (status === 'registration') return 'orange'

  return 'gray'
}

const applySearch = () => {
  currentPage.value = 1
  searchQuery.value = searchInput.value.trim()
}

const onStatusChange = () => {
  currentPage.value = 1
}
</script>

<style scoped>
.tournaments-page {
  gap: 1.4rem;
  padding: 1.6rem 0 2rem;
}

.tournaments-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1.5rem;
}

.tournaments-hero-copy {
  min-width: 0;
}

.breadcrumb-label {
  display: inline-flex;
  align-items: center;
  gap: 0.7rem;
  margin-bottom: 0.75rem;
  color: var(--accent-strong);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.tournaments-hero h1 {
  margin: 0;
  max-width: 760px;
  color: var(--foreground);
  font-size: var(--text-4xl);
  line-height: var(--text-4xl--line-height);
  font-family: var(--font-display);
  font-weight: 800;
}

.tournaments-hero .section-subtitle {
  margin: 0.45rem 0 0;
  max-width: 780px;
  font-size: var(--text-base);
  line-height: var(--text-base--line-height);
}

.hero-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: flex-end;
  align-items: center;
}

.tournaments-stat-card strong {
  color: var(--foreground);
  font-family: var(--font-display);
  font-weight: 800;
}

.tournaments-stat-card span {
  color: var(--muted-foreground);
  font-weight: 700;
  white-space: nowrap;
}

.create-plus {
  font-weight: 800;
  line-height: 1;
}

.tournaments-rule {
  height: 1px;
  margin: 0.7rem 0 0.9rem;
  background: var(--line-soft);
}

.tournaments-section {
  min-width: 0;
}

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
  margin: 2rem 0 0.45rem;
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

.filters-wrapper {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 0.8rem;
  align-items: center;
}

.filters {
  display: flex;
  gap: 0.4rem;
  justify-content: flex-end;
}

.search-wrapper {
  display: flex;
  gap: 0.45rem;
  min-width: 0;
}

.search-input {
  flex: 1;
  min-width: 0;
}

.search-button {
  flex: 0 0 auto;
}

.tournaments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 0.9rem;
}

.tounament-title {
  margin: 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-weight: 800;
  word-break: break-word;
  font-size: var(--text-xl);
  line-height: var(--text-xl--line-height);
}

.tournament-top {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  min-height: 156px;
}

.tournament-banner {
  width: 100%;
  aspect-ratio: 16 / 8;
  object-fit: cover;
  border-radius: 10px;
  border: 1px solid var(--line-soft);
  background: var(--background);
}

.tournament-info {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.tournaments-description {
  flex: 1;
  margin: 0;
  color: var(--muted-foreground);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  word-break: break-word;
}

.tournament-card {
  padding: 0.95rem;
  background: var(--muted);
}

.tournaments-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  color: var(--muted-foreground);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
}

.tournaments-date {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tournaments-date p:first-child {
  font-size: var(--text-xs);
  line-height: var(--text-xs--line-height);
}

.tournaments-date p {
  margin: 0;
}

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

  .tournaments-hero,
  .section-head,
  .empty-row {
    align-items: stretch;
    flex-direction: column;
  }

  .tournaments-hero {
    gap: 1rem;
  }

  .tournaments-hero h1 {
    font-size: var(--text-3xl);
    line-height: var(--text-3xl--line-height);
  }

  .tournaments-hero .section-subtitle {
    font-size: var(--text-sm);
    line-height: var(--text-sm--line-height);
  }

  .hero-actions,
  .section-meta {
    justify-content: flex-start;
    align-items: flex-start;
  }

  .filters-wrapper {
    grid-template-columns: 1fr;
  }

  .filters {
    justify-content: flex-start;
  }

  .tournaments-meta {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
