<template>
  <div class="table-row">
    <div class="team-cell">
      <div class="team-avatar">{{ teamAbbr(submission.team_details.name) }}</div>
      <div>
        <p class="team-name">{{ submission.team_details.name }}</p>
        <p class="team-meta" :title="submission.description">
          {{ truncateText(submission.description || 'No description', 25) }}
        </p>
      </div>
    </div>

    <p class="submitted-on">{{ formatDate(submission.created_at, { showHours: true }) }}</p>

    <div class="assigned-cell">
      <ui-badge v-for="juryId in assigned ?? []" :key="juryId" variant="primary">
        {{ juryLabel(juryId) }}
      </ui-badge>
      <span v-if="!assigned?.length" class="empty-state">No jury assigned</span>
    </div>

    <div class="actions-cell">
      <ui-select
        multiple
        min-width="150px"
        v-model="assigned!"
        :options="juryOptions"
        placeholder="Assign jury"
        class="jury-select"
        :is-error="isFailedToFetchJury"
        :error="juryFetchErrorMessage"
        :is-loading="isFetchingJury"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import UiBadge from '@/components/ui/UiBadge'
import UiSelect, { type SelectOption } from '@/components/ui/UiSelect'
import { formatDate } from '@/lib/date'
import { truncateText } from '@/lib/utils'
import type { JuryAssignSubmission } from '../../../../composables/useJuryAssign'

defineProps<{
  submission: JuryAssignSubmission
  juryOptions: SelectOption[]
  isFailedToFetchJury: boolean
  juryFetchErrorMessage?: string
  isFetchingJury: boolean
  teamAbbr: (teamName: string) => string
  juryLabel: (value: number) => string
}>()

const assigned = defineModel<number[]>('assigned', { default: [] })
</script>

<style scoped>
.table-row {
  display: grid;
  grid-template-columns: 2.5fr 2fr 2.3fr 2fr;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-top: 1px solid var(--border);
}

.table-row:first-child {
  border-top: 0;
}

.team-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.team-avatar {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: var(--primary-foreground);
  background: var(--primary);
  flex: 0 0 auto;
}

.team-name {
  margin: 0;
  font-weight: 700;
}

.team-meta {
  margin: 0.15rem 0 0;
  color: var(--muted-foreground);
  font-size: 0.92rem;
}

.submitted-on {
  margin: 0;
  color: var(--muted-foreground);
}

.assigned-cell {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.4rem;
  min-height: 2.6rem;
}

.empty-state {
  color: var(--muted-foreground);
  font-size: 0.92rem;
}

.actions-cell {
  display: flex;
  justify-content: flex-end;
}

.jury-select {
  min-width: 220px;
}

@media (max-width: 820px) {
  .table-row {
    grid-template-columns: 1fr;
    row-gap: 0.75rem;
  }

  .actions-cell {
    justify-content: flex-start;
  }
}
</style>
