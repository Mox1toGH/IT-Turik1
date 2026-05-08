<template>
  <ui-card class="assignment-card">
    <template #header>
      <div class="card-header">
        <div>
          <h3 class="team-name">{{ teamName }}</h3>
          <p class="round-name">{{ assignment.round_details.name }}</p>
        </div>
        <div class="badges">
          <ui-badge variant="gray">Round</ui-badge>
          <ui-badge :variant="assignment.is_evaluated ? 'green' : 'orange'">
            {{ assignment.is_evaluated ? 'Evaluated' : 'Pending' }}
          </ui-badge>
        </div>
      </div>
    </template>

    <div class="card-body">
      <div class="links">
        <a v-if="githubUrl" :href="githubUrl" target="_blank" rel="noopener noreferrer">GitHub</a>
        <a v-if="demoUrl" :href="demoUrl" target="_blank" rel="noopener noreferrer">Demo</a>
      </div>
      <p class="description">{{ description }}</p>
      <evaluation-summary v-if="assignment.evaluation" :evaluation="assignment.evaluation" />
    </div>

    <template #footer>
      <div class="card-footer">
        <ui-button size="sm" variant="secondary" @click="toggleForm">
          {{ showForm ? 'Close' : assignment.evaluation ? 'Edit Evaluation' : 'Evaluate' }}
        </ui-button>
      </div>
      <div v-if="showForm" class="form-wrap">
        <evaluation-form
          :assignment="assignment"
          :existing-evaluation="assignment.evaluation"
          @cancel="showForm = false"
          @success="handleSuccess"
        />
      </div>
    </template>
  </ui-card>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { JuryAssignmentData } from '@/api/services/evaluation/types'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import EvaluationForm from './EvaluationForm.vue'
import EvaluationSummary from './EvaluationSummary.vue'
import { truncateText } from '@/lib/utils'

interface Props {
  assignment: JuryAssignmentData
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'evaluated'): void
}>()

const showForm = ref(false)

const submissionDetails = computed(
  () =>
    props.assignment.submission_details as {
      description?: string
      github_url?: string
      demo_video_url?: string
      live_demo_url?: string
      team_details?: { name?: string }
    },
)

const teamName = computed(() => submissionDetails.value.team_details?.name ?? `Team #${props.assignment.submission}`)
const githubUrl = computed(() => submissionDetails.value.github_url ?? '')
const demoUrl = computed(() => submissionDetails.value.live_demo_url ?? submissionDetails.value.demo_video_url ?? '')
const description = computed(() => truncateText(submissionDetails.value.description ?? 'No description', 180))

const toggleForm = () => {
  showForm.value = !showForm.value
}

const handleSuccess = () => {
  showForm.value = false
  emit('evaluated')
}
</script>

<style scoped>
.assignment-card {
  background: var(--muted);
  border-color: var(--border);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.8rem;
  border-bottom: 1px solid var(--border);
  padding-bottom: 0.8rem;
}

.team-name {
  margin: 0;
}

.round-name {
  margin: 0.35rem 0 0;
  color: var(--muted-foreground);
}

.badges {
  display: flex;
  gap: 0.45rem;
  flex-wrap: wrap;
}

.card-body {
  display: grid;
  gap: 0.75rem;
}

.links {
  display: flex;
  gap: 0.9rem;
  flex-wrap: wrap;
}

.links a {
  color: var(--primary);
  font-weight: 700;
}

.description {
  margin: 0;
  line-height: 1.5;
  color: var(--foreground);
  word-break: break-word;
}

.card-footer {
  display: flex;
  justify-content: flex-end;
}

.form-wrap {
  margin-top: 0.8rem;
  padding-top: 0.8rem;
  border-top: 1px solid var(--border);
}

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
  }

  .card-footer {
    justify-content: stretch;
  }
}
</style>
