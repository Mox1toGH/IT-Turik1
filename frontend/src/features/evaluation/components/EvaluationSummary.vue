<template>
  <div class="summary">
    <div class="scores">
      <div v-for="item in evaluation.scores" :key="item.criterion_id" class="score-row">
        <span class="criterion">{{ item.criterion_name ?? item.criterion_id }}</span>
        <span class="value">{{ item.score }}</span>
      </div>
    </div>

    <div class="totals">
      <p><strong>Total:</strong> {{ evaluation.total_score }}</p>
      <p><strong>Final:</strong> {{ evaluation.final_score }}</p>
    </div>

    <p v-if="evaluation.comment" class="comment">{{ evaluation.comment }}</p>
  </div>
</template>

<script setup lang="ts">
import type { EvaluationData } from '@/api/services/evaluation/types'

interface Props {
  evaluation: EvaluationData
}

defineProps<Props>()
</script>

<style scoped>
.summary {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
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

.totals {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  padding-top: 0.4rem;
  border-top: 1px solid var(--border);
}

.totals p {
  margin: 0;
}

.comment {
  margin: 0;
  color: var(--muted-foreground);
  line-height: 1.45;
  word-break: break-word;
}
</style>
