<template>
  <ui-section title="Submissions by Round" description="Projects grouped by tournament round">
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
                <div
                  v-for="assignment in submission.assignments"
                  :key="assignment.id"
                  v-show="assignment.evaluation"
                  class="eval-zone"
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
                </div>
              </div>
            </details>
          </ui-card>
        </div>
      </details>
    </div>
    <p v-else class="empty-state">No submissions found.</p>
  </ui-section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import UiCard from '@/components/ui/UiCard'
import UiSection from '@/components/ui/UiSection'
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
.accordion-list {
  display: grid;
  gap: 0;
}

.accordion-item {
  border-top: 1px solid var(--border);
  overflow: hidden;
}

.accordion-item:last-child {
  border-bottom: 1px solid var(--border);
}

.accordion-item > summary {
  cursor: pointer;
  list-style: none;
  display: flex;
  justify-content: space-between;
  gap: 0.6rem;
  padding: 0.75rem 0.25rem;
  font-weight: 600;
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
  background: var(--subtle);
  color: var(--muted-foreground);
}

.submissions-grid {
  display: grid;
  gap: 0.75rem;
  padding: 0.8rem 0;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
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

.eval-zone {
  padding: 0.8rem;
  border-radius: var(--radius-sm);
  background: var(--subtle);
}

.eval-zone p {
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
</style>
