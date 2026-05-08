<template>
  <div class="summary">
    <div class="metric">
      <div class="metric-head">
        <p><strong>Total:</strong> {{ evaluation.total_score }}</p>
        <p class="range">{{ minScore }} - {{ maxScore }}</p>
      </div>

      <div class="criteria-track" role="img" aria-label="Total score by criteria">
        <div
          v-for="(segment, index) in segments"
          :key="segment.id"
          class="criteria-segment"
          :style="{ width: `${segment.widthPercent}%` }"
          :title="`${segment.name}: ${segment.score} / ${segment.max}`"
        >
          <div
            class="criteria-fill"
            :style="{
              width: `${segment.fillPercent}%`,
              backgroundColor: palette[index % palette.length],
            }"
          />
        </div>
      </div>
    </div>

    <div class="metric">
      <div class="metric-head">
        <p><strong>Final:</strong> {{ evaluation.final_score }}</p>
        <p class="range">{{ minScore }} - {{ maxScore }}</p>
      </div>

      <div class="final-track">
        <div class="final-fill" :style="{ width: `${finalPercent}%` }" />
      </div>
    </div>

    <div class="scores">
      <div v-for="item in evaluation.scores" :key="item.criterion_id" class="score-row">
        <span class="criterion">{{ item.criterion_name ?? item.criterion_id }}</span>
        <span class="value">{{ item.score }}</span>
      </div>
    </div>

    <p v-if="evaluation.comment" class="comment">{{ evaluation.comment }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { EvaluationData, RoundCriterion } from '@/api/services/evaluation/types'

interface Props {
  evaluation: EvaluationData
  criteria: RoundCriterion[]
}

const props = defineProps<Props>()

const palette = [
  '#3b82f6',
  '#22c55e',
  '#f59e0b',
  '#ef4444',
  '#8b5cf6',
  '#14b8a6',
  '#f97316',
]

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

const segments = computed(() => {
  const totalMax = maxScore.value || 1
  return props.criteria.map((criterion) => {
    const max = Number(criterion.max_score || 0)
    const rawScore = scoreByCriterion.value.get(criterion.id) ?? 0
    const score = Math.max(0, Math.min(rawScore, max))
    return {
      id: criterion.id,
      name: criterion.name,
      max,
      score,
      widthPercent: (max / totalMax) * 100,
      fillPercent: max ? (score / max) * 100 : 0,
    }
  })
})

const finalPercent = computed(() => {
  if (!maxScore.value) return 0
  const clamped = Math.max(0, Math.min(Number(props.evaluation.final_score || 0), maxScore.value))
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

.criteria-track,
.final-track {
  height: 12px;
  border-radius: 999px;
  overflow: hidden;
  border: 1px solid var(--border);
  display: flex;
  background: color-mix(in srgb, var(--muted) 70%, transparent);
}

.criteria-segment {
  height: 100%;
  border-right: 1px solid color-mix(in srgb, var(--border) 60%, transparent);
}

.criteria-segment:last-child {
  border-right: none;
}

.criteria-fill {
  height: 100%;
}

.final-fill {
  height: 100%;
  background: linear-gradient(
    90deg,
    #3b82f6 0%,
    #22c55e 22%,
    #f59e0b 45%,
    #ef4444 70%,
    #8b5cf6 100%
  );
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
}

.criterion {
  color: var(--muted-foreground);
}

.comment {
  margin: 0;
  color: var(--muted-foreground);
  line-height: 1.45;
  word-break: break-word;
}
</style>
