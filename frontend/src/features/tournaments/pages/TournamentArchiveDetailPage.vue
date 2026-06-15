<template>
  <section class="page-shell">
    <ui-skeleton-loader :loading="isLoading">
      <template #skeleton>
        <div class="skeleton-stack">
          <ui-skeleton variant="rect" height="260px" />
          <div class="skeleton-stats">
            <ui-skeleton v-for="i in 4" :key="`stats-${i}`" variant="rect" height="96px" />
          </div>
          <ui-skeleton variant="rect" height="220px" />
          <ui-skeleton variant="rect" height="220px" />
        </div>
      </template>

      <template #default>
        <div v-if="archive" class="content-stack">
          <ui-card class="hero-card">
            <div class="hero" :style="heroStyle">
              <div class="hero-overlay" />
              <div class="hero-content">
                <p class="hero-kicker">Tournament Archive</p>
                <h1 class="hero-title">{{ archive.name }}</h1>
                <p class="hero-dates">{{ tournamentDateRange }}</p>
                <div class="hero-actions">
                  <ui-button asLink to="/tournaments/archive" size="sm" variant="secondary">Back</ui-button>
                  <ui-button asLink :to="`/tournaments/${id}`" size="sm" variant="secondary"
                    >Open tournament</ui-button
                  >
                </div>
              </div>
            </div>
          </ui-card>

          <ui-card class="section-block">
            <template #header>
              <div class="section-head">
                <h2>Description</h2>
                <p class="section-note">Tournament summary</p>
              </div>
            </template>
            <p class="description-text">{{ archive.description || 'No description provided.' }}</p>
          </ui-card>

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
                <p class="stat-value">{{ archive.rounds?.length ?? 0 }}</p>
              </ui-card>
              <ui-card class="stat-card">
                <p class="stat-label">Submissions</p>
                <p class="stat-value">{{ submissions.length }}</p>
              </ui-card>
              <ui-card class="stat-card">
                <p class="stat-label">Winner</p>
                <p class="stat-value">{{ winnerName }}</p>
              </ui-card>
            </div>
          </ui-card>

          <ui-card class="section-block">
            <template #header>
              <div class="section-head">
                <h2>Final Standings</h2>
                <p class="section-note">Saved final ranking</p>
              </div>
            </template>
            <ui-card v-if="archive.standings?.length" class="table-wrap">
              <div class="table-row table-head">
                <span>Rank</span>
                <span>Team</span>
                <span>Total Score</span>
              </div>
              <div
                v-for="row in archive.standings"
                :key="`${row.rank}-${row.team.id}`"
                class="table-row"
                :class="rankClass(row.rank)"
              >
                <span class="rank-pill">#{{ row.rank }}</span>
                <span>{{ row.team.name }}</span>
                <span>{{ formatScore(row.total_score) }}</span>
              </div>
            </ui-card>
            <ui-card v-else>
              <p class="empty-state">No saved standings.</p>
            </ui-card>
          </ui-card>

          <ui-card class="section-block">
            <template #header>
              <div class="section-head">
                <h2>Rounds Timeline</h2>
                <p class="section-note">Schedule and criteria per round</p>
              </div>
            </template>
            <div v-if="archive.rounds?.length" class="rounds-list">
              <ui-card v-for="round in archive.rounds" :key="round.id" class="round-card">
                <p class="round-title">{{ round.name }}</p>
                <p class="round-meta">{{ formatDateRange(round.start_date, round.end_date) }}</p>
                <p class="round-meta">Start: {{ formatDateTime(round.start_date) }}</p>
                <p class="round-meta">End: {{ formatDateTime(round.end_date) }}</p>
                <p class="round-meta">Criteria: {{ round.criteria?.length ?? 0 }}</p>
              </ui-card>
            </div>
            <ui-card v-else>
              <p class="empty-state">No rounds found.</p>
            </ui-card>
          </ui-card>

          <ui-card class="section-block">
            <template #header>
              <div class="section-head">
                <h2>Submissions by Round</h2>
                <p class="section-note">Projects grouped by tournament round</p>
              </div>
            </template>
            <div v-if="groupedSubmissions.length" class="accordion-list">
              <details v-for="group in groupedSubmissions" :key="group.roundId" class="accordion-item">
                <summary>
                  <span class="summary-title">{{ group.roundName }}</span>
                  <span class="summary-count">{{ group.items.length }} submissions</span>
                </summary>
                <div class="submissions-grid">
                  <ui-card v-for="submission in group.items" :key="submission.id" class="submission-card">
                    <p><strong>Team:</strong> {{ submission.team_details.name }}</p>
                    <p>
                      <strong>GitHub:</strong>
                      <a :href="submission.github_url" target="_blank" rel="noopener noreferrer">{{ submission.github_url }}</a>
                    </p>
                    <p v-if="submission.demo_video_url">
                      <strong>Demo:</strong>
                      <a :href="submission.demo_video_url" target="_blank" rel="noopener noreferrer">{{ submission.demo_video_url }}</a>
                    </p>
                    <p v-if="submission.live_demo_url">
                      <strong>Live:</strong>
                      <a :href="submission.live_demo_url" target="_blank" rel="noopener noreferrer">{{ submission.live_demo_url }}</a>
                    </p>

                    <details v-if="hasEvaluations(submission)" class="eval-details">
                      <summary>Evaluations</summary>
                      <div class="eval-list">
                        <ui-card
                          v-for="assignment in submission.assignments"
                          :key="assignment.id"
                          v-show="assignment.evaluation"
                          class="eval-card"
                        >
                          <p><strong>Jury:</strong> {{ assignment.jury?.full_name || assignment.jury?.username || 'Unknown' }}</p>
                          <p><strong>Final score:</strong> {{ formatScore(assignment.evaluation?.final_score) }}</p>
                          <p><strong>Total score:</strong> {{ formatScore(assignment.evaluation?.total_score) }}</p>
                          <p v-if="assignment.evaluation?.comment"><strong>Comment:</strong> {{ assignment.evaluation.comment }}</p>
                          <div v-if="assignment.evaluation?.scores?.length">
                            <p><strong>Criteria scores:</strong></p>
                            <ul class="scores-list">
                              <li v-for="score in assignment.evaluation.scores" :key="`${assignment.id}-${score.criterion_id}`">
                                {{ score.criterion_name }}: {{ score.score }}
                              </li>
                            </ul>
                          </div>
                        </ui-card>
                      </div>
                    </details>
                  </ui-card>
                </div>
              </details>
            </div>
            <ui-card v-else>
              <p class="empty-state">No submissions found.</p>
            </ui-card>
          </ui-card>

          <ui-card class="section-block">
            <template #header>
              <div class="section-head">
                <h2>Participating Teams</h2>
                <p class="section-note">Teams registered in this archive</p>
              </div>
            </template>
            <div v-if="archive.teams?.length" class="team-grid">
              <ui-card v-for="team in archive.teams" :key="team.id" class="team-chip">{{ team.name }}</ui-card>
            </div>
            <ui-card v-else>
              <p class="empty-state">No participating teams found.</p>
            </ui-card>
          </ui-card>
        </div>
      </template>
    </ui-skeleton-loader>
  </section>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import { useRoute } from 'vue-router'
import { computed } from 'vue'
import {
  useGetTournamentArchive,
  useListTournamentArchiveSubmissions,
} from '@/api/tournaments/tournaments'

const route = useRoute()
const id = Number(route.params.id)
const { data, isLoading } = useGetTournamentArchive(id)
const { data: submissionsData } = useListTournamentArchiveSubmissions(id)

const archive = computed(() => data.value)
const submissions = computed(() => submissionsData.value ?? [])

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
  if (!start && !end) return 'Dates not specified'
  return `${formatDate(start)} - ${formatDate(end)}`
}

const formatDateTime = (value?: string | null) => {
  if (!value) return 'N/A'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'N/A'
  return new Intl.DateTimeFormat(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

const tournamentDateRange = computed(() =>
  formatDateRange(archive.value?.start_date, archive.value?.end_date),
)

const heroStyle = computed(() => {
  const banner = archive.value?.banner
  if (banner) {
    return {
      backgroundImage: `linear-gradient(120deg, rgb(15 23 42 / 70%), rgb(30 41 59 / 30%)), url(${banner})`,
    }
  }
  return {
    backgroundImage:
      'linear-gradient(120deg, color-mix(in srgb, var(--primary) 45%, transparent), color-mix(in srgb, var(--muted) 85%, transparent))',
  }
})

const winnerName = computed(() => {
  const winner = archive.value?.standings?.find((item) => item.rank === 1)
  return winner?.team?.name ?? 'TBD'
})

const groupedSubmissions = computed(() => {
  const groups = new Map<number, { roundId: number; roundName: string; items: typeof submissions.value }>()

  submissions.value.forEach((submission) => {
    const roundId = submission.round_details.id
    const roundName = submission.round_details.name || `Round #${roundId}`
    if (!groups.has(roundId)) {
      groups.set(roundId, { roundId, roundName, items: [] })
    }
    groups.get(roundId)?.items.push(submission)
  })

  return Array.from(groups.values())
})

const hasEvaluations = (submission: (typeof submissions.value)[number]) =>
  submission.assignments.some((assignment) => assignment.evaluation)

const formatScore = (score?: number | string | null) => {
  if (score === null || score === undefined || score === '') return '-'
  const normalized = typeof score === 'number' ? score : Number(score)
  if (Number.isNaN(normalized)) return '-'
  return Number.isInteger(normalized) ? String(normalized) : normalized.toFixed(2)
}

const rankClass = (rank: number) => {
  if (rank === 1) return 'rank-gold'
  if (rank === 2) return 'rank-silver'
  if (rank === 3) return 'rank-bronze'
  return ''
}
</script>

<style scoped>
.page-shell {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding-bottom: 1rem;
}

.skeleton-stack {
  display: grid;
  gap: 0.9rem;
}

.skeleton-stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.8rem;
}

.content-stack {
  display: grid;
  gap: 1.2rem;
}

.hero-card {
  overflow: hidden;
  padding: 0;
  border: 1px solid color-mix(in srgb, var(--line-soft) 70%, transparent);
}

.hero {
  position: relative;
  border-radius: 12px;
  min-height: 300px;
  background-size: cover;
  background-position: center;
  padding: 1.4rem;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgb(2 6 23 / 8%), rgb(2 6 23 / 68%));
}

.hero-content {
  position: relative;
  z-index: 1;
  color: white;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  max-width: 820px;
  min-height: 100%;
}

.hero-kicker,
.hero-dates,
.hero-title {
  margin: 0;
}

.hero-kicker {
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 0.8rem;
  opacity: 0.85;
}

.hero-title {
  font-size: clamp(1.45rem, 2.8vw, 2.2rem);
  line-height: 1.2;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: auto;
  padding-top: 0.75rem;
}

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

.description-text {
  margin: 0;
  color: var(--foreground);
  line-height: 1.5;
  overflow-wrap: anywhere;
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

.table-wrap {
  overflow: hidden;
  padding: 0;
  border: 1px solid var(--line-soft);
}

.table-row {
  display: grid;
  grid-template-columns: 80px 1fr 160px;
  gap: 0.5rem;
  padding: 0.65rem 0.85rem;
  border-top: 1px solid color-mix(in srgb, var(--line-soft) 85%, transparent);
  align-items: center;
}

.table-head {
  border-top: 0;
  font-weight: 600;
  background: var(--muted);
}

.rank-pill {
  width: fit-content;
  border-radius: 999px;
  padding: 0.15rem 0.55rem;
  background: color-mix(in srgb, var(--muted) 65%, transparent);
}

.rank-gold .rank-pill {
  background: #f6d365;
  color: #3a2d00;
}

.rank-silver .rank-pill {
  background: #dce1e8;
  color: #1f2937;
}

.rank-bronze .rank-pill {
  background: #e8b28d;
  color: #4b2a12;
}

.rounds-list,
.team-grid,
.submissions-grid {
  display: grid;
  gap: 0.75rem;
}

.rounds-list {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.round-card {
  border: 1px solid color-mix(in srgb, var(--line-soft) 75%, transparent);
  background: linear-gradient(180deg, var(--card-background, transparent), color-mix(in srgb, var(--muted) 35%, transparent));
}

.round-title,
.round-meta {
  margin: 0;
}

.round-title {
  font-weight: 600;
}

.round-meta {
  color: var(--muted-foreground);
}

.accordion-list {
  display: grid;
  gap: 0.7rem;
}

.accordion-item {
  border: 1px solid var(--line-soft);
  border-radius: 10px;
  background: var(--card-background, transparent);
  overflow: hidden;
}

.accordion-item > summary {
  cursor: pointer;
  list-style: none;
  display: flex;
  justify-content: space-between;
  gap: 0.6rem;
  padding: 0.75rem 0.9rem;
  font-weight: 600;
  background: var(--muted);
}

.accordion-item > summary::marker,
.eval-details > summary::marker {
  content: '';
}

.accordion-item > summary::after,
.eval-details > summary::after {
  content: '+';
  font-weight: 700;
  margin-left: auto;
  opacity: 0.72;
}

.accordion-item[open] > summary::after,
.eval-details[open] > summary::after {
  content: '-';
}

.summary-title {
  overflow-wrap: anywhere;
}

.summary-count {
  font-size: 0.84rem;
  font-weight: 700;
  border-radius: 999px;
  padding: 0.15rem 0.52rem;
  background: color-mix(in srgb, var(--background) 75%, transparent);
}

.accordion-item > summary::-webkit-details-marker {
  display: none;
}

.submissions-grid {
  padding: 0.8rem;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.submission-card {
  background: linear-gradient(135deg, var(--muted), color-mix(in srgb, var(--background) 86%, transparent)) !important;
  border: 1px solid color-mix(in srgb, var(--line-soft) 72%, transparent);
}

.submission-card p {
  margin: 0;
}

.submission-card a {
  color: var(--primary);
  overflow-wrap: anywhere;
}

.eval-details {
  margin-top: 0.5rem;
}

.eval-details > summary {
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.eval-list {
  display: grid;
  gap: 0.5rem;
  margin-top: 0.45rem;
}

.eval-card {
  background: var(--background, white) !important;
  border: 1px solid color-mix(in srgb, var(--line-soft) 65%, transparent);
}

.eval-card p {
  margin: 0;
}

.scores-list {
  margin: 0;
  padding-left: 1rem;
}

.team-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.team-chip {
  text-align: center;
  font-weight: 600;
  background: linear-gradient(
    135deg,
    color-mix(in srgb, var(--muted) 78%, transparent),
    color-mix(in srgb, var(--background) 88%, transparent)
  ) !important;
  border: 1px solid color-mix(in srgb, var(--line-soft) 70%, transparent);
}

.empty-state {
  margin: 0;
  color: var(--muted-foreground);
}

@media (max-width: 980px) {
  .stats-grid,
  .skeleton-stats {
    grid-template-columns: 1fr;
  }

  .rounds-list,
  .team-grid,
  .submissions-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .hero {
    min-height: 260px;
    padding: 1rem;
  }

  .section-note {
    width: 100%;
  }

  .table-row {
    grid-template-columns: 62px 1fr 95px;
    font-size: 0.83rem;
    padding: 0.6rem;
  }
}
</style>
