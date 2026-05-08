<template>
  <ui-card>
    <template #header>
      <div class="submissions-header">
        <h2>My submissions</h2>
        <ui-select
          v-model="filterOption"
          align-to="right"
          multiple
          min-width="200px"
          placeholder="Select round"
          :options="filterOptions"
          :is-loading="isLoadingRounds"
          :is-error="isRoundsError"
          :error="parsedRoundsError?.message"
        />
      </div>
    </template>

    <ui-skeleton-loader :loading="isLoadingSubmissions">
      <template #skeleton>
        <div class="submissions-list">
          <ui-card v-for="i in 3" :key="i" class="submission-card">
            <template #header>
              <div class="submission-header">
                <div class="left-side">
                  <div class="left-side-icon">
                    <FileCheckIcon width="20" />
                  </div>

                  <div class="round-info">
                    <p class="text-muted">Round</p>
                    <ui-skeleton width="140px" />
                  </div>
                </div>

                <div class="right-side">
                  <div class="round-info">
                    <p class="text-muted">submitted on</p>
                    <ui-skeleton width="120px" />
                  </div>

                  <div class="round-info">
                    <p class="text-muted">status</p>
                    <ui-skeleton width="120px" />
                  </div>
                </div>
              </div>
            </template>

            <template #default>
              <ui-skeleton width="120px" />
              <ui-skeleton width="180px" />
              <ui-skeleton width="140px" />
            </template>

            <template #footer>
              <div class="submission-footer">
                <div class="submission-links">
                  <ui-skeleton width="80px" />
                  <ui-skeleton width="80px" />
                </div>
              </div>
            </template>
          </ui-card>
        </div>
      </template>

      <template #default>
        <div class="submissions-list">
          <ui-card v-if="filteredSubmissions.length === 0" class="empty-card">
            <p class="empty-error">No submissions found</p>
          </ui-card>

          <ui-card
            v-else
            v-for="submission in filteredSubmissions"
            :key="submission.id"
            class="submission-card"
          >
            <template #header>
              <div class="submission-header">
                <div class="left-side">
                  <div class="left-side-icon">
                    <FileCheckIcon width="20" />
                  </div>

                  <div class="round-info">
                    <p class="text-muted">Round</p>
                    <p>{{ submission.round_details.name }}</p>
                  </div>
                </div>

                <div class="right-side">
                  <div class="round-info">
                    <p class="text-muted">submitted on</p>
                    <p class="text-muted">{{ formatDate(submission.created_at) }}</p>
                  </div>

                  <div class="round-info">
                    <p class="text-muted">status</p>
                    <ui-badge :variant="badgeVariant(submission.round_details.status)">{{
                      submissionStatus(submission.round_details.status)
                    }}</ui-badge>
                  </div>
                </div>
              </div>
            </template>

            <template #default>
              <large-text-modal
                title="Round description"
                :text="submission.description"
                max-length="200"
                style="max-width: 800px"
              >
                <template #trigger="{ toggleOpen }">
                  <p class="text-muted" :title="submission.description" @click="toggleOpen">
                    {{ truncateText(submission.description, 200) }}
                  </p>
                </template>
              </large-text-modal>
            </template>

            <template #footer>
              <div class="submission-footer">
                <div class="submission-links">
                  <a :href="submission.github_url" target="_blank" class="submission-link"
                    >Github</a
                  >
                  <a :href="submission.demo_video_url" target="_blank" class="submission-link"
                    >Demo</a
                  >
                </div>

                <ui-button
                  size="sm"
                  v-if="submission.round_details.status === 'active'"
                  @click="isEditOpen = true"
                  >Edit Submission</ui-button
                >
                <EditSubmissionModal
                  v-model="isEditOpen"
                  :tournament-id="props.tournamentId"
                  :submission-id="submission.id"
                  :default-values="{
                    github_url: submission.github_url,
                    demo_video_url: submission.demo_video_url,
                    description: submission.description,
                  }"
                />
              </div>

              <div
                v-if="submissionEvaluations(submission).length > 0"
                class="submission-results"
              >
                <p class="text-muted">
                  Result:
                  <strong>{{ averageFinalScore(submission).toFixed(2) }}</strong>
                </p>

                <div
                  v-for="assignment in submissionEvaluations(submission)"
                  :key="assignment.id"
                  class="submission-result-item"
                >
                  <p>
                    {{ assignment.jury.full_name || assignment.jury.username }}:
                    {{ assignment.evaluation?.final_score }}
                  </p>
                  <p v-if="assignment.evaluation?.comment" class="text-muted">
                    {{ assignment.evaluation.comment }}
                  </p>
                </div>
              </div>
            </template>
          </ui-card>
        </div>
      </template>
    </ui-skeleton-loader>
  </ui-card>
</template>

<script setup lang="ts">
import type { RoundStatus, TournamentId } from '@/api/dbTypes'
import { parseApiError } from '@/api/errors'
import { useTeamSubmissions, useTournamentRounds } from '@/api/queries/tournaments'
import LargeTextModal from '@/components/shared/LargeTextModal.vue'
import UiBadge, { type Variants } from '@/components/ui/UiBadge.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiSelect from '@/components/ui/UiSelect.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import FileCheckIcon from '@/icons/FileCheckIcon.vue'
import { formatDate } from '@/lib/date'
import { truncateText } from '@/lib/utils'
import { computed, ref } from 'vue'
import EditSubmissionModal from './tournament-submissions/EditSubmissionModal.vue'

interface Props {
  tournamentId: TournamentId
}

const props = defineProps<Props>()

const isEditOpen = ref(false)

const { data: submissions, isLoading: isLoadingSubmissions } = useTeamSubmissions({
  tournamentId: props.tournamentId,
})

const {
  data: rounds,
  isLoading: isLoadingRounds,
  isError: isRoundsError,
  error: roundsError,
} = useTournamentRounds({ id: props.tournamentId })
const parsedRoundsError = computed(() => parseApiError(roundsError.value))

const filterOptions = computed(() =>
  rounds.value?.map((round) => ({
    value: round.name,
    label: round.name,
  })),
)
const filterOption = ref<string[]>([])
const filteredSubmissions = computed(() => {
  if (!filterOption.value.length) {
    return submissions.value ?? []
  }

  return (submissions.value ?? []).filter((submission) =>
    filterOption.value.includes(submission.round_details.name),
  )
})

const submissionStatus = (roundStatus: RoundStatus) => {
  return roundStatus === 'active' ? 'Active' : 'Closed'
}
const badgeVariant = (roundStatus: RoundStatus): Variants => {
  return roundStatus === 'active' ? 'primary' : 'red'
}

const submissionEvaluations = (submission: NonNullable<typeof submissions.value>[number]) => {
  return (submission.assignments ?? []).filter((assignment) => assignment.evaluation)
}

const averageFinalScore = (submission: NonNullable<typeof submissions.value>[number]) => {
  const evaluations = submissionEvaluations(submission)
  if (!evaluations.length) return 0
  const total = evaluations.reduce(
    (sum, assignment) => sum + Number(assignment.evaluation?.final_score ?? 0),
    0,
  )
  return total / evaluations.length
}
</script>

<style scoped>
.submissions-list {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.submissions-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.6rem;
}

.submission-card {
  background: var(--muted);
}

.submission-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.8rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border);
}

.left-side-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 50px;
  height: 50px;
  padding: 0.7rem;
  background: color-mix(in srgb, var(--primary) 10%, transparent);
  color: var(--primary);
  border-radius: 50%;
}

.round-info {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.right-side,
.left-side {
  display: flex;
  gap: 2rem;
  align-items: center;
}

.submission-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
}

.submission-links {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.submission-link {
  color: var(--brand-700);
  font-weight: 700;
}

.submission-results {
  margin-top: 0.8rem;
  padding-top: 0.8rem;
  border-top: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.submission-result-item {
  background: color-mix(in srgb, var(--primary) 5%, transparent);
  border-radius: var(--radius);
  padding: 0.55rem 0.7rem;
}

@media (max-width: 625px) {
  .submission-header {
    flex-direction: column;
    gap: 1rem;
  }

  .left-side {
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border);
  }
}
</style>
