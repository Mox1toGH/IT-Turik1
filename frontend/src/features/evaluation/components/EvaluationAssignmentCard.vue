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
        <p v-if="githubUrl" class="link-row">
          <span class="link-label">GitHub:</span>
          <a :href="githubUrl" target="_blank" rel="noopener noreferrer">{{ githubUrl }}</a>
        </p>
        <p v-if="demoVideoUrl" class="link-row">
          <span class="link-label">Demo Video:</span>
          <a :href="demoVideoUrl" target="_blank" rel="noopener noreferrer">{{ demoVideoUrl }}</a>
        </p>
        <p v-if="liveDemoUrl" class="link-row">
          <span class="link-label">Live Demo:</span>
          <a :href="liveDemoUrl" target="_blank" rel="noopener noreferrer">{{ liveDemoUrl }}</a>
        </p>
      </div>

      <p class="description">{{ description }}</p>
      <evaluation-summary
        v-if="assignment.evaluation"
        :evaluation="assignment.evaluation"
        :criteria="assignment.round_details.criteria"
      />
    </div>

    <template #footer>
      <div class="card-footer">
        <ui-button v-if="canEditEvaluation" size="sm" variant="secondary" @click="toggleForm">
          {{ assignment.evaluation ? 'Edit Evaluation' : 'Evaluate' }}
        </ui-button>
      </div>
    </template>
  </ui-card>

  <ui-modal v-model="showForm" scrollable>
    <template #title>
      <div>
        <h3>{{ assignment.evaluation ? 'Edit Evaluation' : 'Set Evaluation' }}</h3>
        <p class="modal-subtitle">{{ teamName }} · {{ assignment.round_details.name }}</p>
      </div>
    </template>

    <evaluation-form
      :assignment="assignment"
      :existing-evaluation="assignment.evaluation"
      @cancel="showForm = false"
      @success="handleSuccess"
    />
  </ui-modal>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiModal from '@/components/ui/UiModal.vue'
import EvaluationForm from './EvaluationForm.vue'
import EvaluationSummary from './EvaluationSummary.vue'
import type { JuryAssignment } from '@/api/.ts.schemas'

interface Props {
  assignment: JuryAssignment
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

const teamName = computed(
  () => submissionDetails.value.team_details?.name ?? `Team #${props.assignment.submission}`,
)
const githubUrl = computed(() => submissionDetails.value.github_url ?? '')
const demoVideoUrl = computed(() => submissionDetails.value.demo_video_url ?? '')
const liveDemoUrl = computed(() => submissionDetails.value.live_demo_url ?? '')
const description = computed(() => submissionDetails.value.description ?? 'No description')
const canEditEvaluation = computed(
  () => props.assignment.round_details.status === 'submission_closed',
)

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
  display: grid;
  gap: 0.35rem;
  border-bottom: 1px solid var(--border);
  padding-bottom: 0.8rem;
}

.links a {
  color: var(--primary);
  word-break: break-all;
}

.link-row {
  margin: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.link-label {
  color: var(--muted-foreground);
  font-weight: 700;
}

.description {
  margin: 0;
  line-height: 1.5;
  color: var(--foreground);
  word-break: break-word;
  border-bottom: 1px solid var(--border);
  padding-bottom: 0.8rem;
}

.card-footer {
  display: flex;
  justify-content: flex-end;
}

.modal-subtitle {
  margin: 0.35rem 0 0;
  color: var(--muted-foreground);
  font-size: 0.9rem;
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
