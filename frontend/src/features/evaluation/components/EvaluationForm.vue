<template>
  <form class="form" @submit.prevent="handleSubmit">
    <div class="criteria-list">
      <div
        v-for="criterion in assignment.round_details.criteria"
        :key="criterion.id"
        class="criterion-row"
      >
        <div class="criterion-head">
          <p class="criterion-name">{{ criterion.name }}</p>
          <p class="criterion-max">Max: {{ criterion.max_score }}</p>
        </div>

        <ui-input
          v-model="scoresMap[criterion.id]"
          type="number"
          :min="0"
          :max="criterion.max_score"
          :is-invalid="hasCriterionError(criterion.id, criterion.max_score)"
        />
      </div>
    </div>

    <div class="totals">
      <p>
        Total: <strong>{{ total }}</strong>
      </p>
      <p class="hint">All scores must be within criterion limits</p>
    </div>

    <div class="field">
      <p class="field-label">Comment</p>
      <ui-text-area v-model="comment" placeholder="Optional feedback for the team" />
    </div>

    <div class="actions">
      <ui-button size="sm" variant="secondary" type="button" @click="emit('cancel')"
        >Cancel</ui-button
      >
      <ui-button size="sm" type="submit" :disabled="hasAnyError || isPending">
        {{ existingEvaluation ? 'Save Changes' : 'Submit Evaluation' }}
      </ui-button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiTextArea from '@/components/ui/UiTextArea.vue'
import type { JuryAssignment, ScoreItem } from '@/api/.ts.schemas'
import {
  useCreateJuryEvaluation,
  useUpdateJuryEvaluation,
  type GetJuryEvaluationQueryResult,
} from '@/api/evaluation/evaluation'

interface Props {
  assignment: JuryAssignment
  existingEvaluation?: GetJuryEvaluationQueryResult | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'success'): void
  (e: 'cancel'): void
}>()

const scoresMap = reactive<Record<string, number>>(
  props.assignment.round_details.criteria.reduce<Record<string, number>>((acc, criterion) => {
    const existingScore = props.existingEvaluation?.scores?.find(
      (score) => score.criterion_id === criterion.id,
    )?.score
    acc[criterion.id] = typeof existingScore === 'number' ? existingScore : 0
    return acc
  }, {}),
)

const comment = ref(props.existingEvaluation?.comment ?? '')

const scoreItems = computed<ScoreItem[]>(() =>
  props.assignment.round_details.criteria.map((criterion) => ({
    criterion_id: criterion.id,
    criterion_name: criterion.name,
    score: Number(scoresMap[criterion.id] ?? 0),
  })),
)

const total = computed(() => scoreItems.value.reduce((sum, item) => sum + item.score, 0))

const hasCriterionError = (criterionId: string, maxScore: number) => {
  const score = Number(scoresMap[criterionId])
  return Number.isNaN(score) || score < 0 || score > maxScore
}

const hasAnyError = computed(() =>
  props.assignment.round_details.criteria.some((criterion) =>
    hasCriterionError(criterion.id, criterion.max_score),
  ),
)

const createMutation = useCreateJuryEvaluation()
const updateMutation = useUpdateJuryEvaluation()
const isPending = computed(() => createMutation.isPending.value || updateMutation.isPending.value)

const tournamentId = computed(
  () =>
    props.assignment.round_details.tournament ??
    (props.assignment.submission_details as { round_details?: { tournament?: number } })
      .round_details?.tournament ??
    0,
)

const handleSubmit = () => {
  if (hasAnyError.value || !tournamentId.value) return

  const body = {
    tournament_id: tournamentId.value,
    assignment: props.assignment.id,
    scores: scoreItems.value,
    comment: comment.value.trim() || undefined,
  }

  if (props.existingEvaluation?.id) {
    updateMutation.mutate(
      {
        id: props.existingEvaluation.id,
        data: body,
      },
      {
        onSuccess: () => {
          emit('success')
        },
      },
    )
    return
  }

  createMutation.mutate(
    { data: body },
    {
      onSuccess: () => {
        emit('success')
      },
    },
  )
}
</script>

<style scoped>
.form {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
}

.criteria-list {
  display: grid;
  gap: 0.75rem;
}

.criterion-row {
  display: grid;
  gap: 0.45rem;
}

.criterion-head {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.criterion-name,
.criterion-max {
  margin: 0;
}

.criterion-max {
  color: var(--muted-foreground);
}

.totals {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  padding-top: 0.65rem;
  border-top: 1px solid var(--border);
}

.totals p {
  margin: 0;
}

.hint {
  color: var(--muted-foreground);
  font-size: 0.9rem;
}

.field {
  display: grid;
  gap: 0.4rem;
}

.field-label {
  margin: 0;
  color: var(--muted-foreground);
}

.actions {
  display: flex;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 0.55rem;
}
</style>
