<template>
  <div class="summary">
    <div class="scores">
      <div v-for="item in normalizedScores" :key="item.criterion_id" class="score-row">
        <span class="criterion">
          <span
            class="criterion-dot"
            :style="{ backgroundColor: item.color }"
            aria-hidden="true"
          ></span>
          {{ item.criterion_name }}
        </span>
        <span class="value">{{ item.score }} / {{ item.max }}</span>
      </div>
    </div>

    <div v-if="evaluation.comment" class="comment-box">
      <p class="comment-label">Comment</p>
      <p class="comment">{{ evaluation.comment }}</p>
    </div>

    <div class="metric">
      <div class="metric-head">
        <p><strong>Total:</strong> {{ evaluation.total_score }}</p>
        <p class="range">{{ minScore }} - {{ maxScore }}</p>
      </div>

      <ui-segmented-progress-bar
        :percent="totalPercent"
        :segments="usedSegments"
        aria-label="Total score by criteria"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import UiSegmentedProgressBar from '@/components/ui/UiSegmentedProgressBar.vue'
import type { Criterion, JuryAssignment } from '@/api/.ts.schemas'

interface Props {
  evaluation: JuryAssignment['evaluation']
  criteria: Criterion[]
}

const props = defineProps<Props>()

const palette = ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#14b8a6', '#f97316']

const minScore = 0
const maxScore = computed(() =>
  props.criteria.reduce((sum, criterion) => sum + Number(criterion.max_score || 0), 0),
)

const scoreByCriterion = computed(() => {
  const map = new Map<string, number>()
  props.evaluation.scores.forEach((item) => {
    map.set(item.criterion_id, Number(item.score || 0))
  })
  return map
})

const normalizedScores = computed(() =>
  props.criteria.map((criterion, index) => {
    const max = Number(criterion.max_score || 0)
    const rawScore = scoreByCriterion.value.get(criterion.id) ?? 0
    const score = Math.max(0, Math.min(rawScore, max))
    return {
      id: criterion.id,
      criterion_id: criterion.id,
      criterion_name: criterion.name,
      max,
      score,
      color: palette[index % palette.length],
    }
  }),
)

const scoredSum = computed(() =>
  normalizedScores.value.reduce((sum, item) => sum + Number(item.score || 0), 0),
)

const usedSegments = computed(() => {
  const usedTotal = scoredSum.value || 1
  return normalizedScores.value.map((item) => ({
    id: item.criterion_id,
    widthPercent: (item.score / usedTotal) * 100,
    title: `${item.criterion_name}: ${item.score} / ${item.max}`,
    color: item.color,
  }))
})

const totalPercent = computed(() => {
  if (!maxScore.value) return 0
  const clamped = Math.max(0, Math.min(Number(props.evaluation.total_score || 0), maxScore.value))
  return (clamped / maxScore.value) * 100
})
</script>

<style scoped>
.summary {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.metric {
  display: grid;
  gap: 0.35rem;
}

.metric-head {
  display: flex;
  justify-content: space-between;
  gap: 0.8rem;
}

.metric-head p {
  margin: 0;
}

.range {
  color: var(--muted-foreground);
}

.scores {
  display: grid;
  gap: 0.4rem;
}

.score-row {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  color: var(--foreground);
  padding: 0.45rem 0.55rem;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: color-mix(in srgb, var(--muted) 55%, transparent);
}

.criterion {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  color: var(--foreground);
  font-weight: 600;
}

.criterion-dot {
  width: 0.55rem;
  height: 0.55rem;
  border-radius: 50%;
  flex-shrink: 0;
}

.value {
  color: var(--muted-foreground);
  font-variant-numeric: tabular-nums;
}

.comment {
  margin: 0;
  color: var(--foreground);
  line-height: 1.45;
  word-break: break-word;
}

.comment-box {
  border: 1px solid color-mix(in srgb, var(--primary) 35%, var(--border));
  background: color-mix(in srgb, var(--primary) 8%, transparent);
  border-radius: 12px;
  padding: 0.75rem;
  display: grid;
  gap: 0.35rem;
}

.comment-label {
  margin: 0;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--primary);
  font-weight: 700;
}
</style>
