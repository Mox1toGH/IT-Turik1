<template>
  <section class="page-shell home-page">
    <header class="home-hero">
      <div class="hero-copy">
        <div class="breadcrumb-label">
          <span>Workspace</span>
          <span aria-hidden="true">/</span>
          <span>Home</span>
        </div>

        <h1>
          Welcome back,
          <ui-skeleton-loader :loading="isLoading" class="name-loader">
            <template #skeleton>
              <ui-skeleton variant="rect" width="160px" />
            </template>

            <span>{{ displayName }}</span>
          </ui-skeleton-loader>
        </h1>

        <p class="section-subtitle">
          Manage your profile, track competition readiness, and jump back into the work that
          matters.
        </p>
      </div>

      <div class="hero-actions">
        <ui-card v-for="item in heroStats" :key="item.label" variant="stat" class="hero-stat">
          <span class="text-base">{{ item.label }}:</span>
          <strong class="text-base">{{ item.value }}</strong>
        </ui-card>
      </div>
    </header>

    <div class="home-rule" aria-hidden="true"></div>

    <StatsPreview :user="user" />

    <section class="dashboard-grid" aria-label="Account overview">
      <ui-card v-if="isTeamRole" class="info-card quick-card" variant="form">
        <template #header>
          <div class="panel-header">
            <span class="step-marker">01</span>
            <div>
              <h2>Quick access</h2>
              <p class="text-muted">Current tournament links for your team.</p>
            </div>
          </div>
        </template>

        <ui-skeleton-loader class="panel-body" :loading="isQuickBlockLoading" min-height="120px">
          <template #skeleton>
            <div class="skeleton-stack">
              <ui-skeleton variant="rect" width="50%" />
              <ui-skeleton variant="rect" width="60%" />
              <ui-skeleton variant="rect" width="45%" />
            </div>
          </template>

          <ul class="data-list">
            <li>
              <span>Tournament</span>
              <RouterLink
                v-if="activeTournament"
                class="quick-link"
                :to="`/tournaments/${activeTournament.id}`"
              >
                {{ activeTournament.name }}
              </RouterLink>
              <span v-else>-</span>
            </li>
            <li>
              <span>Current task</span>
              <RouterLink
                v-if="activeTournament && currentRound?.name"
                class="quick-link"
                :to="`/tournaments/${activeTournament.id}?section=rounds`"
              >
                {{ currentRound.name }}
              </RouterLink>
              <span v-else>{{ currentRound?.name ?? '-' }}</span>
            </li>
            <li>
              <span>Latest submission</span>
              <RouterLink
                v-if="activeTournament && lastSubmission?.round_details?.name"
                class="quick-link"
                :to="`/tournaments/${activeTournament.id}?section=submissions`"
              >
                {{ lastSubmission.round_details.name }}
              </RouterLink>
              <span v-else>{{ lastSubmission?.round_details?.name ?? '-' }}</span>
            </li>
          </ul>
        </ui-skeleton-loader>
      </ui-card>

      <ui-card class="info-card" variant="form" :is-error="isLoadingError">
        <template #error>
          <div class="empty-state">
            <p>Failed to fetch account info (code: {{ profileError?.code }})</p>
          </div>
        </template>

        <template #header>
          <div class="panel-header">
            <span class="step-marker">02</span>
            <div>
              <h2>Account details</h2>
              <p class="text-muted">Profile identity and team membership.</p>
            </div>
          </div>
        </template>

        <ui-skeleton-loader class="panel-body" :loading="isLoading">
          <template #skeleton>
            <div class="skeleton-stack">
              <ui-skeleton variant="rect" width="55%" />
              <ui-skeleton variant="rect" width="65%" />
              <ui-skeleton variant="rect" width="35%" />
              <ui-skeleton variant="rect" width="70%" />
            </div>
          </template>

          <dl class="detail-list">
            <div v-for="item in accountDetails" :key="item.label">
              <dt>{{ item.label }}</dt>
              <dd>{{ item.value }}</dd>
            </div>
          </dl>
        </ui-skeleton-loader>
      </ui-card>

      <ui-card class="info-card" variant="form" :is-error="isLoadingError">
        <template #error>
          <div class="empty-state">
            <p>Failed to fetch profile status (code: {{ profileError?.code }})</p>
          </div>
        </template>

        <template #header>
          <div class="panel-header">
            <span class="step-marker">03</span>
            <div>
              <h2>Quick status</h2>
              <p class="text-muted">Readiness checks for your account.</p>
            </div>
          </div>
        </template>

        <ui-skeleton-loader class="panel-body" :loading="isLoading" min-height="90px">
          <template #skeleton>
            <div class="skeleton-stack">
              <ui-skeleton variant="rect" width="45%" />
              <ui-skeleton variant="rect" width="38%" />
              <ui-skeleton variant="rect" width="42%" />
            </div>
          </template>

          <ul class="status-list">
            <li v-for="item in statusItems" :key="item.label">
              <span class="status-dot" :class="{ ready: item.ready }" aria-hidden="true"></span>
              <span>{{ item.label }}</span>
              <strong>{{ item.ready ? 'Ready' : 'Missing' }}</strong>
            </li>
          </ul>
        </ui-skeleton-loader>
      </ui-card>
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import StatsPreview from '@/components/stats/StatsPreview.vue'
import { useGetUserProfile } from '@/api/accounts/accounts'
import {
  useGetCurrentTask,
  useListMyTeamSubmissions,
  useListTournaments,
} from '@/api/tournaments/tournaments'

const { data: user, isLoading, isLoadingError, error: profileError } = useGetUserProfile()

const displayName = computed(() => user.value?.full_name || user.value?.username || 'User')
const profileReady = computed(() => Boolean(user.value?.full_name && user.value?.city))
const teamNames = computed(() => (user.value?.teams || []).map((team) => team.name).join(', '))
const isTeamRole = computed(() => user.value?.role === 'team')
const myTeamIds = computed(() => new Set((user.value?.teams ?? []).map((team) => team.id)))
const accountDetails = computed(() => [
  { label: 'Username', value: user.value?.username ?? '-' },
  { label: 'Email', value: user.value?.email ?? '-' },
  { label: 'Role', value: user.value?.role ?? '-' },
  { label: 'Teams', value: teamNames.value || '-' },
])
const statusItems = computed(() => [
  { label: 'Profile ready', ready: profileReady.value },
  { label: 'City set', ready: Boolean(user.value?.city) },
  { label: 'Phone set', ready: Boolean(user.value?.phone) },
])
const heroStats = computed(() => [
  { label: 'Role', value: user.value?.role ?? '-' },
  { label: 'Teams', value: String(user.value?.teams?.length ?? 0) },
])

const { data: tournamentsResponse, isLoading: isLoadingActiveTournament } = useListTournaments(
  computed(() => ({
    page: 1,
    page_size: 100,
    status: 'registration,running',
  })),
  {
    query: { enabled: computed(() => Boolean(isTeamRole.value)) },
  },
)
const activeTournament = computed(() =>
  (tournamentsResponse.value?.data ?? []).find((tournament) =>
    myTeamIds.value.has(tournament.registered_team?.id ?? -1),
  ),
)
const activeTournamentId = computed(() => activeTournament.value?.id ?? 0)
const shouldFetchCurrentRound = computed(
  () =>
    Boolean(isTeamRole.value && activeTournamentId.value) &&
    activeTournament.value?.status === 'running',
)

const { data: currentRound, isLoading: isLoadingCurrentRound } = useGetCurrentTask(
  { tournament_id: activeTournamentId.value },
  {
    query: {
      enabled: shouldFetchCurrentRound,
      retry: false,
    },
  },
)

const { data: submissions, isLoading: isLoadingSubmissions } = useListMyTeamSubmissions(
  activeTournamentId,
  {
    query: {
      enabled: computed(() =>
        Boolean(isTeamRole.value && activeTournamentId.value && user.value?.role === 'team'),
      ),
    },
  },
)

const lastSubmission = computed(() => {
  const list = submissions.value ?? []
  if (list.length === 0) return null
  return list.reduce((latest, current) =>
    new Date(current.created_at).getTime() > new Date(latest.created_at).getTime()
      ? current
      : latest,
  )
})

const isQuickBlockLoading = computed(
  () =>
    isLoading.value ||
    isLoadingActiveTournament.value ||
    isLoadingCurrentRound.value ||
    isLoadingSubmissions.value,
)
</script>

<style scoped>
.home-page {
  display: grid;
  gap: 1.4rem;
  padding: 1.6rem 0 2rem;
}

.home-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1.5rem;
}

.hero-copy {
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

.home-hero h1 {
  margin: 0;
  max-width: 800px;
  color: var(--foreground);
  font-family: var(--font-display);
  font-size: var(--text-4xl);
  line-height: var(--text-4xl--line-height);
  font-weight: 800;
}

.name-loader {
  display: inline-block;
}

.home-hero .section-subtitle {
  max-width: 760px;
  margin: 0.45rem 0 0;
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

.hero-stat {
  display: flex;
}

.hero-stat strong {
  color: var(--foreground);
  font-family: var(--font-display);
  font-weight: 800;
}

.hero-stat span {
  color: var(--muted-foreground);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  font-weight: 700;
  white-space: nowrap;
}

.home-rule {
  height: 1px;
  margin: 0.7rem 0 0.9rem;
  background: var(--line-soft);
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
  align-items: stretch;
}

.quick-card {
  grid-column: span 1;
}

.panel-header {
  min-width: 0;
}

.panel-body {
  display: block;
}

.panel-body :deep(> div) {
  min-width: 0;
}

.skeleton-stack {
  display: grid;
  gap: 0.65rem;
}

:deep(.data-list),
:deep(.status-list),
:deep(.detail-list) {
  display: grid;
  gap: 0.65rem;
  padding: 0;
  margin: 0;
  list-style: none;
}

:deep(.data-list li),
:deep(.detail-list div),
:deep(.status-list li) {
  display: grid;
  gap: 0.75rem;
  align-items: center;
  min-width: 0;
  padding: 0.8rem;
  border: 1px solid var(--line-soft);
  border-radius: 12px;
  background: color-mix(in srgb, var(--card) 92%, var(--foreground) 8%);
}

:deep(.data-list li),
:deep(.detail-list div) {
  grid-template-columns: minmax(0, 0.75fr) minmax(0, 1.25fr);
}

:deep(.data-list span),
:deep(.detail-list dt) {
  color: var(--muted-foreground);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  font-weight: 700;
}

:deep(.data-list li > :last-child),
:deep(.detail-list dd) {
  min-width: 0;
  margin: 0;
  overflow: hidden;
  color: var(--foreground);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  font-weight: 800;
  text-align: right;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:deep(.status-list li) {
  grid-template-columns: auto minmax(0, 1fr) auto;
}

:deep(.status-list span:not(.status-dot)) {
  color: var(--foreground);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  font-weight: 700;
}

:deep(.status-list strong) {
  color: var(--muted-foreground);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
}

:deep(.status-dot) {
  width: 0.7rem;
  height: 0.7rem;
  display: inline-block;
  border-radius: 999px;
  background: var(--warning);
}

:deep(.status-dot.ready) {
  background: var(--primary);
}

:deep(.quick-link) {
  color: var(--accent-strong);
  font-weight: 800;
  text-decoration: none;
}

:deep(.quick-link:hover) {
  text-decoration: underline;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 126px;
  text-align: center;
}

.empty-state p {
  margin: 0;
  color: var(--muted-foreground);
}

@media (max-width: 980px) {
  .dashboard-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .quick-card {
    grid-column: auto;
  }
}

@media (max-width: 760px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  .home-page {
    padding: 1rem 1rem 2rem;
  }

  .home-hero {
    align-items: stretch;
    flex-direction: column;
    gap: 1rem;
  }

  .home-hero h1 {
    font-size: var(--text-3xl);
    line-height: var(--text-3xl--line-height);
  }

  .home-hero .section-subtitle {
    font-size: var(--text-sm);
    line-height: var(--text-sm--line-height);
  }

  .hero-actions {
    justify-content: flex-start;
  }

  :deep(.data-list li),
  :deep(.detail-list div) {
    grid-template-columns: 1fr;
  }

  :deep(.data-list li > :last-child),
  :deep(.detail-list dd) {
    text-align: left;
  }
}
</style>
