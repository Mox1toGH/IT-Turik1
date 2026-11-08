<template>
  <ui-query-block :query="tournamentQuery" :title="isEdit ? 'tournament' : undefined">
    <ui-query-field>
      <template #skeleton>
        <div class="form-skeleton">
          <ui-skeleton variant="rect" height="220px" />
          <ui-skeleton variant="rect" height="140px" />
          <ui-skeleton variant="rect" height="200px" />
        </div>
      </template>
      <form class="tournament-form" @submit.prevent="handleSubmit">
        <ui-card class="form-panel">
          <div class="panel-header">
            <span class="step-marker">01</span>
            <div>
              <h2>Basics</h2>
              <p class="text-muted">Name the tournament and describe what teams are joining.</p>
            </div>
          </div>

          <div class="basics-fields-grid">
            <label class="form-item">
              <span class="form-label">Tournament name</span>
              <ui-input
                id="tournamentName"
                v-model="form.fields.value.name"
                placeholder="Enter tournament name"
                required
                :isInvalid="!!form.errors.value.name"
                @blur="form.validateField('name')"
              />
              <small v-if="form.errors.value.name" class="text-error">{{
                form.errors.value.name
              }}</small>
            </label>

            <label class="form-item description-field">
              <span class="form-label">Description</span>
              <ui-text-area
                id="tournamentDescription"
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
          </div>
        </ui-card>

        <ui-card class="form-panel">
          <div class="panel-header">
            <span class="step-marker">02</span>
            <div>
              <h2>Capacity</h2>
              <p class="text-muted">Control how many teams can enter and how large they must be.</p>
            </div>
          </div>

          <div class="settings-row">
            <label class="form-item">
              <span class="form-label">Max teams</span>
              <ui-number-input
                id="maxTeams"
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
              <ui-number-input
                id="minTeamMembers"
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
        </ui-card>

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

        <div class="form-actions">
          <ui-button type="submit" size="lg" :disabled="isPending">
            {{ isPending ? pendingText : submitText }}
          </ui-button>
        </div>
      </form>
    </ui-query-field>
  </ui-query-block>
</template>

<script setup lang="ts">
import { computed, unref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { UiQueryBlock, UiQueryField } from '@/components/query'
import UiButton from '@/components/ui/UiButton'
import UiCard from '@/components/ui/UiCard'
import UiDatePicker from '@/components/ui/UiDatePicker'
import UiInput from '@/components/ui/UiInput'
import UiNumberInput from '@/components/ui/UiNumberInput'
import UiSkeleton from '@/components/ui/UiSkeleton'
import UiTextArea from '@/components/ui/UiTextArea'
import UiTimePicker from '@/components/ui/UiTimePicker'
import { useNotification } from '@/composables/useNotification'
import { useForm } from '@/composables/useForm'
import { CreateTournamentSchema } from '@/schemas/tournaments.schema'
import {
  useCreateTournament,
  useGetTournament,
  useUpdateTournament,
} from '@/api/tournaments/tournaments'
import {
  createTournamentFormDefaults,
  toTime,
  toTournamentPayload,
  type TournamentFormFields as TournamentFormValues,
} from '../../composables/useTournamentForm'

const props = withDefaults(
  defineProps<{
    mode: 'create' | 'edit'
    tournamentId?: number
  }>(),
  { tournamentId: undefined },
)

const isEdit = computed(() => props.mode === 'edit')
const router = useRouter()
const { showNotification } = useNotification()
const form = useForm<TournamentFormValues>(
  CreateTournamentSchema as never,
  createTournamentFormDefaults(),
)

const tournamentQuery = useGetTournament(
  computed(() => props.tournamentId ?? 0),
  {
    query: { enabled: isEdit },
  },
)
const { data: tournament } = tournamentQuery
const { mutate: createTournament, isPending: isCreating } = useCreateTournament()
const { mutate: updateTournament, isPending: isUpdating } = useUpdateTournament()

const isPending = computed(() => (isEdit.value ? isUpdating.value : isCreating.value))
const submitText = computed(() => (isEdit.value ? 'Save changes' : 'Create tournament'))
const pendingText = computed(() => (isEdit.value ? 'Saving...' : 'Creating...'))

watch(
  tournament,
  (value) => {
    if (!isEdit.value || !value) return
    form.hydrate({
      name: value.name,
      description: value.description,
      startDate: new Date(value.start_date),
      startTime: toTime(value.start_date),
      endDate: new Date(value.end_date),
      endTime: toTime(value.end_date),
      max_teams: value.max_teams ?? 2,
      min_team_members: value.min_team_members ?? 2,
    })
  },
  { immediate: true },
)

function handleSubmit() {
  const values = unref(form.fields)
  if (!form.validate()) return

  const data = toTournamentPayload(values)
  if (isEdit.value) {
    if (!props.tournamentId) return
    updateTournament(
      { id: props.tournamentId, data },
      {
        onSuccess() {
          showNotification('Tournament updated successfully.', 'success')
          void router.push(`/tournaments/${props.tournamentId}`)
        },
        onError(error) {
          for (const [field, messages] of Object.entries(error?.details ?? {})) {
            form.setError(
              field,
              Array.isArray(messages) ? (messages[0] ?? 'Invalid value') : messages,
            )
          }
          showNotification(error.message, 'error')
        },
      },
    )
    return
  }

  createTournament(
    { data },
    {
      onSuccess() {
        void router.push('/tournaments')
      },
      onError(error) {
        for (const [field, messages] of Object.entries(error?.details ?? {})) {
          form.setError(
            field,
            Array.isArray(messages) ? (messages[0] ?? 'Invalid value') : messages,
          )
        }
        showNotification(error.message, 'error')
      },
    },
  )
}
</script>

<style scoped>
.form-skeleton {
  display: grid;
  gap: 1.25rem;
  width: 100%;
}

.tournament-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  min-width: 0;
  width: 100%;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
}

.form-panel {
  display: grid;
  gap: 1rem;
}

.panel-header p {
  margin: 0.25rem 0 0;
}

.basics-fields-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
  align-items: start;
}

.description-input {
  min-height: 190px;
  height: 100%;
}

.settings-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.8rem;
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

@media (max-width: 760px) {
  .basics-fields-grid {
    grid-template-columns: 1fr;
  }

  .description-input {
    height: 150px;
    min-height: 150px;
  }
}

@media (max-width: 480px) {
  .settings-row,
  .date-time-group {
    grid-template-columns: 1fr;
  }

  .date-time-group {
    gap: 0.5rem;
  }
}
</style>
