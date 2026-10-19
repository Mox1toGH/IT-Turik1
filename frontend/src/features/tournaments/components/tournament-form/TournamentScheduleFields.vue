<template>
  <ui-card class="form-panel">
    <div class="panel-header">
      <span class="step-marker">03</span>
      <div>
        <h2>Schedule</h2>
        <p class="text-muted">Choose when the tournament opens and closes.</p>
      </div>
    </div>

    <div class="schedule-column">
      <div class="date-time-group">
        <label class="form-item date-part">
          <span class="form-label">Start date</span>
          <ui-date-picker
            v-model="form.fields.value.startDate"
            :isInvalid="!!form.errors.value.startDate"
            required
            @blur="form.validateField('startDate')"
          />
          <small v-if="form.errors.value.startDate" class="text-error">{{
            form.errors.value.startDate
          }}</small>
        </label>

        <label class="form-item time-part">
          <span class="form-label">Time</span>
          <ui-time-picker
            v-model="form.fields.value.startTime"
            @blur="form.validateField('startTime')"
          />
          <small v-if="form.errors.value.startTime" class="text-error">{{
            form.errors.value.startTime
          }}</small>
        </label>
      </div>

      <div class="date-time-group">
        <label class="form-item date-part">
          <span class="form-label">End date</span>
          <ui-date-picker
            v-model="form.fields.value.endDate"
            :isInvalid="!!form.errors.value.endDate"
            required
            @blur="form.validateField('endDate')"
          />
          <small v-if="form.errors.value.endDate" class="text-error">{{
            form.errors.value.endDate
          }}</small>
        </label>

        <label class="form-item time-part">
          <span class="form-label">Time</span>
          <ui-time-picker
            v-model="form.fields.value.endTime"
            @blur="form.validateField('endTime')"
          />
          <small v-if="form.errors.value.endTime" class="text-error">{{
            form.errors.value.endTime
          }}</small>
        </label>
      </div>
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard'
import UiDatePicker from '@/components/ui/UiDatePicker'
import UiTimePicker from '@/components/ui/UiTimePicker'
import type { TournamentFormController } from '../../composables/useTournamentForm'

const props = defineProps<{
  form: TournamentFormController
}>()
const form = { ...props.form }
</script>

<style scoped>
.form-panel {
  display: grid;
  gap: 1rem;
}

.panel-header p {
  margin: 0.25rem 0 0;
}

.schedule-column {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.date-time-group {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 0.8rem;
}

@media (max-width: 480px) {
  .date-time-group {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }
}
</style>
