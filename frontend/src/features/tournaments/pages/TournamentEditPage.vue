<template>
  <ui-card :is-error="isError">
    <template #header>
      <h1 class="section-title">Edit tournament</h1>
    </template>

    <template #error>
      <div style="display: flex; height: 300px; justify-content: center; align-items: center">
        <p>Error while fetching tournament (code: {{ parsedError?.code }})</p>
      </div>
    </template>

    <ui-skeleton-loader :loading="isLoading || isFetching">
      <template #skeleton>
        <div class="tournament-form">
          <ui-skeleton variant="rect" height="90px" />
          <ui-skeleton variant="rect" height="290px" />
          <ui-skeleton variant="rect" height="140px" />
          <ui-skeleton variant="rect" height="140px" />
        </div>
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

        <ui-button type="submit" :disabled="isPending">Save</ui-button>
      </form>
    </ui-skeleton-loader>
  </ui-card>
</template>

<script setup lang="ts">
import { parseApiError } from '@/api/errors'
import type { EditTournamentBody } from '@/api/services/tournaments/types'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiDatePicker from '@/components/ui/UiDatePicker.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiTextArea from '@/components/ui/UiTextArea.vue'
import UiTimePicker from '@/components/ui/UiTimePicker.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import { useForm } from '@/composables/useForm'
import { combineDateAndTime } from '@/lib/date'
import { useEditTournament, useTournamentInfo } from '@/api/queries/tournaments'
import { EditTournamentSchema } from '@/schemas/tournaments.schema'
import { computed, unref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { TournamentId } from '@/api/dbTypes'
import { useNotification } from '@/composables/useNotification'

interface Form {
  name: string
  description: string
  startDate: Date
  startTime: string
  endTime: string
  endDate: Date
  max_teams: number
  min_team_members: number
}

const route = useRoute()
const router = useRouter()
const { showNotification } = useNotification()

const tournamentId = computed(() => Number(route.params.id || 0) as TournamentId)

const form = useForm<Form>(EditTournamentSchema, {
  name: '',
  description: '',
  startDate: new Date(),
  startTime: '00:00',
  endDate: new Date(),
  endTime: '00:00',
  max_teams: 2,
  min_team_members: 2,
})

const {
  data: tournament,
  isLoading,
  isFetching,
  error,
  isError,
} = useTournamentInfo({ id: tournamentId.value })

const { mutate: editTournament, isPending } = useEditTournament()

const parsedError = computed(() => parseApiError(error.value))

const apiToFormFieldMap: Record<string, keyof Form> = {
  start_date: 'startDate',
  end_date: 'endDate',
}

function toPayload(values: Form): EditTournamentBody {
  return {
    name: values.name,
    description: values.description,
    max_teams: values.max_teams,
    min_team_members: values.min_team_members,
    start_date: combineDateAndTime(values.startDate, values.startTime),
    end_date: combineDateAndTime(values.endDate, values.endTime),
  }
}

const toTime = (value: Date | string) => {
  const date = new Date(value)
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${hours}:${minutes}`
}

watch(
  tournament,
  (value) => {
    if (!value) return

    const startDate = new Date(value.start_date)
    const endDate = new Date(value.end_date)

    form.fields.value = {
      name: value.name,
      description: value.description,
      startDate,
      startTime: toTime(value.start_date),
      endDate,
      endTime: toTime(value.end_date),
      max_teams: value.max_teams,
      min_team_members: value.min_team_members,
    }
  },
  { immediate: true },
)

const handleSubmit = () => {
  const values = unref(form.fields)

  if (!form.validate()) return

  editTournament(
    {
      id: tournamentId.value,
      body: toPayload(values),
    },
    {
      onSuccess() {
        showNotification('Tournament updated successfully.', 'success')
        router.push(`/tournaments/${tournamentId.value}`)
      },
      onError: (requestError) => {
        const errorResponse = parseApiError(requestError)

        for (const [apiField, errors] of Object.entries(errorResponse?.details || {})) {
          const formField = apiToFormFieldMap[apiField] ?? apiField
          form.setError(formField as keyof Form, errors?.[0] ?? 'Invalid value')
        }

        if (!Object.keys(errorResponse?.details || {}).length) {
          showNotification(errorResponse?.message || 'Failed to update tournament', 'error')
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
