<template>
  <section class="create-tournament-page page-shell">
    <ui-card class="create-hero">
      <div>
        <p class="section-eyebrow">Tournament workspace</p>
        <h1>Create tournament</h1>
        <p class="section-subtitle">
          Set the public details, team limits, and registration window before rounds are added.
        </p>
      </div>

      <ui-button asLink to="/tournaments" variant="secondary" size="lg" class="back-link">
        Back to tournaments
      </ui-button>
    </ui-card>

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
          <ui-button asLink to="/tournaments" variant="secondary" size="lg">Cancel</ui-button>
          <ui-button type="submit" size="lg" :disabled="isPending">
            {{ isPending ? 'Creating...' : 'Create tournament' }}
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
  </section>
</template>

<script setup lang="ts">
import {
  useCreateTournament,
  type CreateTournamentMutationBody,
} from '@/api/tournaments/tournaments'
import UiButton from '@/components/ui/UiButton.vue'
import UiDatePicker from '@/components/ui/UiDatePicker.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiNumberInput from '@/components/ui/UiNumberInput.vue'
import UiTextArea from '@/components/ui/UiTextArea.vue'
import UiTimePicker from '@/components/ui/UiTimePicker.vue'
import { useForm } from '@/composables/useForm'
import { useNotification } from '@/composables/useNotification'
import { combineDateAndTime } from '@/lib/date'
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
  max_teams: 2,
  min_team_members: 2,
})

const router = useRouter()
const { mutate: createTournament, isPending } = useCreateTournament()

const { showNotification } = useNotification()

const apiToFormFieldMap: Record<string, keyof Form> = {
  start_date: 'startDate',
  end_date: 'endDate',
}

function toPayload(values: Form): CreateTournamentMutationBody {
  return {
    name: values.name,
    description: values.description,
    max_teams: values.max_teams,
    min_team_members: values.min_team_members,
    start_date: combineDateAndTime(values.startDate, values.startTime).toISOString(),
    end_date: combineDateAndTime(values.endDate, values.endTime).toISOString(),
  }
}

const handleSubmit = () => {
  const values = unref(form.fields)

  if (!form.validate()) return

  createTournament(
    {
      data: toPayload(values),
    },
    {
      onSuccess() {
        router.push('/tournaments')
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
.create-tournament-page {
  gap: 1.4rem;
  padding: 1.6rem 0 2rem;
}

.create-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1.5rem;
}

.create-hero h1 {
  margin: 0.35rem 0 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-size: var(--text-4xl);
  line-height: var(--text-4xl--line-height);
  font-weight: 800;
}

.create-hero .section-subtitle {
  max-width: 680px;
  margin: 0.45rem 0 0;
}

.back-link {
  flex: 0 0 auto;
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
  display: flex;
  flex-direction: row;
  justify-content: end;
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
  .create-tournament-page {
    padding: 1rem 1rem 2rem;
  }

  .create-hero {
    flex-direction: column;
    align-items: flex-start;
    padding: 1.2rem;
  }

  .create-hero h1 {
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
