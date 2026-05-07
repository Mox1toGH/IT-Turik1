<template>
  <ui-card>
    <template #header>
      <h1 class="section-title">Create tournament</h1>
    </template>

    <form class="tournament-form" @submit.prevent="handleSubmit">
      <label class="form-item name-field">
        <span class="form-label">Team name</span>
        <ui-input
          id="teamName"
          v-model="form.fields.value.name"
          placeholder="Enter tournament name"
          required
          :isInvalid="!!form.errors.value.name"
          @blur="form.validateField('name')"
        />
        <small v-if="form.errors.value.name" class="text-error">{{ form.errors.value.name }}</small>
      </label>

      <label class="form-item description-field">
        <span class="form-label">Description</span>
        <ui-text-area
          id="desc"
          v-model="form.fields.value.description"
          class="description-input"
          required
          :isInvalid="!!form.errors.value.description"
          @blur="form.validateField('description')"
        />
        <small v-if="form.errors.value.description" class="text-error">{{
          form.errors.value.description
        }}</small>
      </label>

      <div class="form-row settings-row">
        <label class="form-item">
          <span class="form-label">Rounds</span>
          <ui-select
            :modelValue="String(form.fields.value.rounds_count)"
            @update:modelValue="(val) => (form.fields.value.rounds_count = Number(val))"
            :options="[
              { value: '1', label: '1' },
              { value: '2', label: '2' },
              { value: '3', label: '3' },
              { value: '4', label: '4' },
            ]"
            required
            @blur="form.validateField('rounds_count')"
          />
          <small v-if="form.errors.value.rounds_count" class="text-error">{{
            form.errors.value.rounds_count
          }}</small>
        </label>

        <label class="form-item" style="grid-column-start: 1">
          <span class="form-label">Max Teams</span>
          <ui-input
            id="maxTeams"
            type="number"
            v-model.number="form.fields.value.max_teams"
            min="2"
            required
            :isInvalid="!!form.errors.value.max_teams"
            @blur="form.validateField('max_teams')"
          />
          <small v-if="form.errors.value.max_teams" class="text-error">{{
            form.errors.value.max_teams
          }}</small>
        </label>

        <label class="form-item">
          <span class="form-label">Min team members</span>
          <ui-input
            type="number"
            v-model.number="form.fields.value.min_team_members"
            min="2"
            required
            :isInvalid="!!form.errors.value.min_team_members"
            @blur="form.validateField('min_team_members')"
          />
          <small v-if="form.errors.value.min_team_members" class="text-error">{{
            form.errors.value.min_team_members
          }}</small>
        </label>
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
              class="time-field"
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
              class="time-field"
              @blur="form.validateField('endTime')"
            />
            <small v-if="form.errors.value.endTime" class="text-error">{{
              form.errors.value.endTime
            }}</small>
          </label>
        </div>
      </div>

      <ui-button type="submit">Create</ui-button>
    </form>
  </ui-card>
</template>

<script setup lang="ts">
import { parseApiError } from '@/api/errors'
import type { CreateTournamentBody } from '@/api/services/tournaments/types'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiDatePicker from '@/components/ui/UiDatePicker.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiSelect from '@/components/ui/UiSelect.vue'
import UiTextArea from '@/components/ui/UiTextArea.vue'
import UiTimePicker from '@/components/ui/UiTimePicker.vue'
import { useForm } from '@/composables/useForm'
import { combineDateAndTime } from '@/lib/date'
import { useCreateTournament } from '@/api/queries/tournaments'
import { CreateTournamentSchema } from '@/schemas/tournaments.schema'
import { unref } from 'vue'
import { useRouter } from 'vue-router'

interface Form {
  name: string
  description: string
  startDate: Date
  startTime: string
  endTime: string
  endDate: Date
  rounds_count: number
  max_teams: number
  min_team_members: number
}

const form = useForm<Form>(CreateTournamentSchema, {
  name: '',
  description: '',
  startDate: new Date(),
  startTime: '00:00',
  endDate: new Date(),
  endTime: '00:00',
  rounds_count: 1,
  max_teams: 2,
  min_team_members: 2,
})

const router = useRouter()
const { mutate: createTournament } = useCreateTournament()

const apiToFormFieldMap: Record<string, keyof Form> = {
  start_date: 'startDate',
  end_date: 'endDate',
}

function toPayload(values: Form): CreateTournamentBody {
  return {
    name: values.name,
    description: values.description,
    rounds_count: values.rounds_count,
    max_teams: values.max_teams,
    min_team_members: values.min_team_members,
    start_date: combineDateAndTime(values.startDate, values.startTime),
    end_date: combineDateAndTime(values.endDate, values.endTime),
  }
}

const handleSubmit = () => {
  const values = unref(form.fields)

  if (!form.validate()) return

  createTournament(
    {
      body: toPayload(values),
    },
    {
      onSuccess() {
        router.push('/tournaments')
      },

      onError: (error) => {
        const parsedError = parseApiError(error)

        for (const [apiField, errors] of Object.entries(parsedError?.details || {})) {
          const formField = apiToFormFieldMap[apiField] ?? apiField
          form.setError(formField as keyof Form, errors?.[0] ?? 'Invalid value')
        }
      },
    },
  )
}
</script>

<style scoped>
.tournament-form {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto auto;
  gap: 1rem;
}

.description-field {
  grid-column: 2;
  grid-row: 1 / 4;
}

.description-input {
  height: 100%;
}

.settings-row {
  grid-column: 1;
  grid-row: 2;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.8rem;
}

.schedule-column {
  grid-column: 1;
  grid-row: 3;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.date-time-group {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 0.8rem;
}

.time-field {
  width: 100%;
}

@media (max-width: 800px) {
  .tournament-form {
    grid-template-columns: 1fr;
    grid-template-rows: auto;
    gap: 1.2rem;
  }

  .name-field,
  .description-field,
  .settings-row,
  .schedule-column {
    grid-column: 1;
    grid-row: auto;
  }

  .description-input {
    height: 150px;
  }
}

@media (max-width: 480px) {
  .date-time-group {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }

  .settings-row {
    grid-template-columns: 1fr;
  }
}
</style>
