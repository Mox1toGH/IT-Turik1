<template>
  <section class="edit-tournament-page page-shell">
    <ui-card class="edit-hero">
      <div>
        <p class="section-eyebrow">Tournament workspace</p>
        <h1>Edit tournament</h1>
        <p class="section-subtitle">
          Update the public details, team limits, and registration window for this tournament.
        </p>
      </div>

      <ui-button
        asLink
        :to="`/tournaments/${tournamentId}`"
        variant="secondary"
        size="lg"
        class="back-link"
      >
        Back to tournament
      </ui-button>
    </ui-card>

    <div v-if="isError" class="error-state">
      <ui-card>
        <p>Error while fetching tournament (code: {{ error?.code }})</p>
      </ui-card>
    </div>

    <ui-skeleton-loader v-else :loading="isLoading || isFetching">
      <template #skeleton>
        <div class="create-layout">
          <div class="tournament-form">
            <ui-skeleton variant="rect" height="220px" />
            <ui-skeleton variant="rect" height="140px" />
            <ui-skeleton variant="rect" height="200px" />
          </div>
          <ui-skeleton variant="rect" height="320px" />
        </div>
      </template>

      <div class="create-layout">
        <form class="tournament-form" @submit.prevent="handleSubmit">
          <ui-card variant="form" class="form-panel basics-panel">
            <div class="panel-header">
              <span class="step-marker">01</span>
              <div>
                <h2>Basics</h2>
                <p class="text-muted">Name the tournament and describe what teams are joining.</p>
              </div>
            </div>

            <label class="form-item">
              <span class="form-label">Tournament name</span>
              <ui-input
                id="teamName"
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
          </ui-card>

          <ui-card variant="form" class="form-panel">
            <div class="panel-header">
              <span class="step-marker">02</span>
              <div>
                <h2>Capacity</h2>
                <p class="text-muted">
                  Control how many teams can enter and how large they must be.
                </p>
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

          <ui-card variant="form" class="form-panel">
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

          <ui-card variant="actions" class="form-actions">
            <ui-button asLink :to="`/tournaments/${tournamentId}`" variant="secondary" size="lg"
              >Cancel</ui-button
            >
            <ui-button type="submit" size="lg" :disabled="isPending">
              {{ isPending ? 'Saving...' : 'Save changes' }}
            </ui-button>
          </ui-card>
        </form>

        <aside class="summary-panel" aria-label="Tournament summary">
          <ui-card variant="stat" class="summary-stat">
            <strong>{{ form.fields.value.max_teams }}</strong>
            <span>Teams</span>
          </ui-card>

          <ui-card variant="form" class="summary-card">
            <p class="section-eyebrow">Draft summary</p>
            <h2>{{ form.fields.value.name || 'Untitled tournament' }}</h2>
            <p class="summary-description text-muted">
              {{ form.fields.value.description || 'Description will appear here as you write.' }}
            </p>

            <div class="summary-list">
              <ui-card variant="inset" class="summary-list-item">
                <span>Team size</span>
                <strong>{{ form.fields.value.min_team_members }}+ members</strong>
              </ui-card>
              <ui-card variant="inset" class="summary-list-item">
                <span>Starts</span>
                <strong>{{ form.fields.value.startTime }}</strong>
              </ui-card>
              <ui-card variant="inset" class="summary-list-item">
                <span>Ends</span>
                <strong>{{ form.fields.value.endTime }}</strong>
              </ui-card>
            </div>
          </ui-card>
        </aside>
      </div>
    </ui-skeleton-loader>
  </section>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton.vue'
import UiDatePicker from '@/components/ui/UiDatePicker.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiNumberInput from '@/components/ui/UiNumberInput.vue'
import UiTextArea from '@/components/ui/UiTextArea.vue'
import UiTimePicker from '@/components/ui/UiTimePicker.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import { useForm } from '@/composables/useForm'
import { combineDateAndTime } from '@/lib/date'
import { EditTournamentSchema } from '@/schemas/tournaments.schema'
import { computed, unref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNotification } from '@/composables/useNotification'
import {
  useGetTournament,
  useUpdateTournament,
  type UpdateTournamentMutationBody,
} from '@/api/tournaments/tournaments'

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

const tournamentId = computed(() => Number(route.params.id || 0))

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

const { data: tournament, isLoading, isFetching, error, isError } = useGetTournament(tournamentId)

const { mutate: editTournament, isPending } = useUpdateTournament()

const apiToFormFieldMap: Record<string, keyof Form> = {
  start_date: 'startDate',
  end_date: 'endDate',
}

function toPayload(values: Form): UpdateTournamentMutationBody {
  return {
    name: values.name,
    description: values.description,
    max_teams: values.max_teams,
    min_team_members: values.min_team_members,
    start_date: combineDateAndTime(values.startDate, values.startTime).toISOString(),
    end_date: combineDateAndTime(values.endDate, values.endTime).toISOString(),
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
      max_teams: value.max_teams ?? 2,
      min_team_members: value.min_team_members ?? 2,
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
      data: toPayload(values),
    },
    {
      onSuccess() {
        showNotification('Tournament updated successfully.', 'success')
        router.push(`/tournaments/${tournamentId.value}`)
      },
      onError: (error) => {
        for (const [apiField, errors] of Object.entries(error?.details || {})) {
          const formField = apiToFormFieldMap[apiField] ?? apiField
          form.setError(formField as keyof Form, errors?.[0] ?? 'Invalid value')
        }

        showNotification(error.message, 'error')
      },
    },
  )
}
</script>

<style scoped>
.edit-tournament-page {
  gap: 1.4rem;
  padding: 1.6rem 0 2rem;
}

.edit-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1.5rem;
}

.edit-hero h1 {
  margin: 0.35rem 0 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-size: var(--text-4xl);
  line-height: var(--text-4xl--line-height);
  font-weight: 800;
}

.edit-hero .section-subtitle {
  max-width: 680px;
  margin: 0.45rem 0 0;
}

.back-link {
  flex: 0 0 auto;
}

.error-state {
  display: flex;
  justify-content: center;
}

.create-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(280px, 0.38fr);
  gap: 1rem;
  align-items: start;
}

.tournament-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-width: 0;
}

.form-panel.card {
  display: grid;
  gap: 1rem;
}

.basics-panel {
  grid-template-columns: minmax(0, 0.85fr) minmax(320px, 1.15fr);
}

.basics-panel .panel-header {
  grid-column: 1 / -1;
}

.panel-header {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

.panel-header h2 {
  margin: 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-size: var(--text-xl);
  line-height: var(--text-xl--line-height);
  font-weight: 800;
}

.panel-header p {
  margin: 0.25rem 0 0;
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

.form-actions {
  position: sticky;
  bottom: 1rem;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.summary-panel {
  position: sticky;
  top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-width: 0;
}

.summary-stat {
  justify-content: flex-start;
}

.summary-stat strong {
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  line-height: var(--text-2xl--line-height);
  font-weight: 800;
}

.summary-stat span {
  color: var(--muted-foreground);
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.summary-card.card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.summary-card h2 {
  margin: 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-size: var(--text-xl);
  line-height: var(--text-xl--line-height);
  font-weight: 800;
}

.summary-description {
  display: -webkit-box;
  min-height: 3.2rem;
  margin: 0;
  overflow: hidden;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.summary-list {
  display: grid;
  gap: 0.65rem;
  padding-top: 0.15rem;
}

.summary-list-item.card {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
}

.summary-list span {
  color: var(--muted-foreground);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  font-weight: 700;
}

.summary-list strong {
  text-align: right;
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
}

@media (max-width: 980px) {
  .create-layout,
  .basics-panel {
    grid-template-columns: 1fr;
  }

  .summary-panel {
    position: static;
  }
}

@media (max-width: 760px) {
  .edit-tournament-page {
    padding: 1rem 1rem 2rem;
  }

  .edit-hero {
    flex-direction: column;
    align-items: flex-start;
    padding: 1.2rem;
  }

  .edit-hero h1 {
    font-size: var(--text-3xl);
    line-height: var(--text-3xl--line-height);
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

  .form-actions {
    position: static;
    flex-direction: column-reverse;
  }
}
</style>
