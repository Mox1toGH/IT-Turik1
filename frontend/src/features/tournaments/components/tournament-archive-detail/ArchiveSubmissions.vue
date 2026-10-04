<template>
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
              <a :href="submission.github_url" target="_blank" rel="noopener noreferrer">{{
                submission.github_url
              }}</a>
            </p>
            <p v-if="submission.demo_video_url">
              <strong>Demo:</strong>
              <a :href="submission.demo_video_url" target="_blank" rel="noopener noreferrer">{{
                submission.demo_video_url
              }}</a>
            </p>
            <p v-if="submission.live_demo_url">
              <strong>Live:</strong>
              <a :href="submission.live_demo_url" target="_blank" rel="noopener noreferrer">{{
                submission.live_demo_url
              }}</a>
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
                  <p>
                    <strong>Jury:</strong>
                    {{ assignment.jury?.full_name || assignment.jury?.username || 'Unknown' }}
                  </p>
                  <p>
                    <strong>Final score:</strong>
                    {{ formatScore(assignment.evaluation?.final_score) }}
                  </p>
                  <p>
                    <strong>Total score:</strong>
                    {{ formatScore(assignment.evaluation?.total_score) }}
                  </p>
                  <p v-if="assignment.evaluation?.comment">
                    <strong>Comment:</strong> {{ assignment.evaluation.comment }}
                  </p>
                  <div v-if="assignment.evaluation?.scores?.length">
                    <p><strong>Criteria scores:</strong></p>
                    <ul class="scores-list">
                      <li
                        v-for="score in assignment.evaluation.scores"
                        :key="`${assignment.id}-${score.criterion_id}`"
                      >
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
</template>

<script setup lang="ts">
import { computed } from 'vue'
import UiCard from '@/components/ui/UiCard.vue'
import { formatScore } from './lib/format'
import { type SubmissionResponse } from '@/api/backendAPINinja.schemas'

type Submission = SubmissionResponse

const props = defineProps<{
  submissions: Submission[]
}>()

const groupedSubmissions = computed(() => {
  const groups = new Map<number, { roundId: number; roundName: string; items: Submission[] }>()

  props.submissions.forEach((submission) => {
    const roundId = submission.round_details.id
    const roundName = submission.round_details.name || `Round #${roundId}`
    if (!groups.has(roundId)) {
      groups.set(roundId, { roundId, roundName, items: [] })
    }
    groups.get(roundId)?.items.push(submission)
  })

  return Array.from(groups.values())
})

const hasEvaluations = (submission: Submission) =>
  submission.assignments.some((assignment) => assignment.evaluation)
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

.accordion-item > summary::-webkit-details-marker {
  display: none;
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

.submissions-grid {
  display: grid;
  gap: 0.75rem;
  padding: 0.8rem;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.submission-card {
  background: linear-gradient(
    135deg,
    var(--muted),
    color-mix(in srgb, var(--background) 86%, transparent)
  ) !important;
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

.empty-state {
  margin: 0;
  color: var(--muted-foreground);
}

@media (max-width: 980px) {
  .submissions-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .section-note {
    width: 100%;
  }
}
</style>
