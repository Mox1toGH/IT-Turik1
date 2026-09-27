<template>
  <section class="create-round-page page-shell">
    <header class="round-hero">
      <div class="round-hero-copy">
        <div class="breadcrumb-label">
          <span>Tournament</span>
          <span aria-hidden="true">/</span>
          <span>Create round</span>
        </div>

        <h1>Create round</h1>
        <p class="section-subtitle">
          Set up the round details, schedule, requirements, and evaluation criteria.
        </p>
      </div>
    </header>

    <div class="round-rule" aria-hidden="true"></div>

    <ui-card variant="panel" class="round-form-card">
      <form class="round-form" @submit.prevent="handleSubmit">
        <div class="form-section form-section-main">
          <div class="form-section-heading">
            <span class="step-marker">01</span>
            <div>
              <h2>Round details</h2>
              <p>Give the round a clear name and describe what participants should expect.</p>
            </div>
          </div>

          <div class="form-grid">
            <label class="form-item title-field">
              <span class="form-label">Name</span>
              <ui-input
                v-model="form.fields.value.name"
                placeholder="Enter round title"
                :isInvalid="!!form.errors.value.name"
                @blur="form.validateField('name')"
              />
              <small v-if="form.errors.value.name" class="text-error">
                {{ form.errors.value.name }}
              </small>
            </label>

            <label class="form-item desc-field">
              <span class="form-label">Description</span>
              <editor-modal
                v-model="form.fields.value.description"
                title="Description"
                addText="Add description"
                editText="Edit description"
                ariaLabel="Description editor"
                @blur="form.validateField('description')"
              />
              <small v-if="form.errors.value.description" class="text-error">
                {{ form.errors.value.description }}
              </small>
            </label>
          </div>
        </div>

        <div class="form-section">
          <div class="form-section-heading">
            <span class="step-marker">02</span>
            <div>
              <h2>Schedule</h2>
              <p>Choose when the round opens and when it ends.</p>
            </div>
          </div>

          <div class="schedule-grid">
            <label class="form-item">
              <span class="form-label">Start date/time</span>

              <div class="datetime-row">
                <ui-date-picker
                  v-model="form.fields.value.start_date"
                  :isInvalid="!!form.errors.value.start_date"
                  @blur="form.validateField('start_date')"
                />

                <ui-input
                  v-model="form.fields.value.start_time"
                  type="time"
                  :isInvalid="!!form.errors.value.start_time"
                  @blur="form.validateField('start_time')"
                />
              </div>

              <small v-if="form.errors.value.start_date" class="text-error">
                {{ form.errors.value.start_date }}
              </small>
              <small v-if="form.errors.value.start_time" class="text-error">
                {{ form.errors.value.start_time }}
              </small>
            </label>

            <label class="form-item">
              <span class="form-label">End date/time</span>

              <div class="datetime-row">
                <ui-date-picker
                  v-model="form.fields.value.end_date"
                  :isInvalid="!!form.errors.value.end_date"
                  @blur="form.validateField('end_date')"
                />

                <ui-input
                  v-model="form.fields.value.end_time"
                  type="time"
                  :isInvalid="!!form.errors.value.end_time"
                  @blur="form.validateField('end_time')"
                />
              </div>

              <small v-if="form.errors.value.end_date" class="text-error">
                {{ form.errors.value.end_date }}
              </small>
              <small v-if="form.errors.value.end_time" class="text-error">
                {{ form.errors.value.end_time }}
              </small>
            </label>
          </div>
        </div>

        <div class="form-section">
          <div class="form-section-heading">
            <span class="step-marker">03</span>
            <div>
              <h2>Requirements</h2>
              <p>Define the technical expectations and required participant qualifications.</p>
            </div>
          </div>

          <div class="requirements-grid">
            <label class="form-item">
              <span class="form-label">Technical requirements</span>
              <editor-modal
                v-model="form.fields.value.tech_requirements"
                title="Technical requirements"
                addText="Add technical requirements"
                editText="Edit technical requirements"
                ariaLabel="Technical requirements editor"
                @blur="form.validateField('tech_requirements')"
              />
              <small v-if="form.errors.value.tech_requirements" class="text-error">
                {{ form.errors.value.tech_requirements }}
              </small>
            </label>

            <label class="form-item">
              <span class="form-label">Must have</span>
              <editor-modal
                v-model="form.fields.value.must_have_requirements"
                title="Must have"
                addText="Add must have"
                editText="Edit must have"
                ariaLabel="Must have editor"
                @blur="form.validateField('must_have_requirements')"
              />
              <small v-if="form.errors.value.must_have_requirements" class="text-error">
                {{ form.errors.value.must_have_requirements }}
              </small>
            </label>
          </div>
        </div>

        <div class="form-section">
          <div class="form-section-heading">
            <span class="step-marker">04</span>
            <div>
              <h2>Evaluation</h2>
              <p>Set the passing threshold and criteria used to evaluate submissions.</p>
            </div>
          </div>

          <div class="evaluation-grid">
            <label class="form-item passing-count-field">
              <span class="form-label">Passing count</span>
              <ui-number-input
                v-model="form.fields.value.passing_count"
                min="0"
                placeholder="Enter passing teams count"
                :isInvalid="!!form.errors.value.passing_count"
                @blur="form.validateField('passing_count')"
              />
              <small v-if="form.errors.value.passing_count" class="text-error">
                {{ form.errors.value.passing_count }}
              </small>
            </label>

            <label class="form-item criteria-field">
              <span class="form-label">Evaluation criteria</span>
              <AddCriteriaModal
                v-model="form.fields.value.criteria"
                @blur="form.validateField('criteria')"
              />
              <small v-if="form.errors.value.criteria" class="text-error">
                {{ form.errors.value.criteria }}
              </small>
            </label>
          </div>
        </div>

        <div class="form-actions">
          <ui-button class="submit-btn" type="submit" size="lg" :disabled="isPending">
            <loading-icon v-if="isPending" />
            <span>Create round</span>
          </ui-button>
        </div>
      </form>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiDatePicker from '@/components/ui/UiDatePicker.vue'
import UiNumberInput from '@/components/ui/UiNumberInput.vue'
import UiInput from '@/components/ui/UiInput.vue'
import AddCriteriaModal from '../components/create-round/modals/AddCriteriaModal.vue'
import EditorModal from '../components/create-round/modals/EditorModal.vue'
import { useForm } from '@/composables/useForm'
import { CreateRoundSchema } from '@/schemas/tournaments.schema'
import type { JSONContent } from '@tiptap/core'
import { useRoute, useRouter } from 'vue-router'
import { useNotification } from '@/composables/useNotification'
import { combineDateAndTime } from '@/lib/date'
import { useCreateRound } from '@/api/tournaments/tournaments'

interface RoundCriteriaItem {
  id: string
  name: string
  description: string
  max_score: number
}

interface Form {
  name: string
  passing_count: number
  tech_requirements: JSONContent | null
  description: JSONContent | null
  must_have_requirements: JSONContent | null
  criteria: RoundCriteriaItem[]
  start_date: Date
  start_time: string
  end_date: Date
  end_time: string
}

const form = useForm<Form>(CreateRoundSchema, {
  name: '',
  passing_count: 2,
  description: null,
  tech_requirements: null,
  must_have_requirements: null,
  criteria: [],
  start_date: new Date(),
  start_time: '00:00',
  end_date: new Date(),
  end_time: '23:59',
})

const route = useRoute()
const router = useRouter()
const { showNotification } = useNotification()
const tournamentId = Number(route.params.id)

const { mutate: createRound, isPending } = useCreateRound()

function handleSubmit() {
  if (!form.validate()) return

  const { start_time, end_time, ...rest } = form.fields.value

  createRound(
    {
      tournamentPk: tournamentId,
      data: {
        tournament: tournamentId,
        ...rest,
        start_date: combineDateAndTime(form.fields.value.start_date, start_time).toISOString(),
        end_date: combineDateAndTime(form.fields.value.end_date, end_time).toISOString(),
      },
    },
    {
      onSuccess: () => {
        router.push({
          path: `/tournaments/${tournamentId}`,
          query: {
            section: 'rounds',
          },
        })
      },
      onError(error) {
        for (const [field, errors] of Object.entries(error?.details || {})) {
          form.setError(field as keyof Form, errors?.[0] ?? 'Invalid value')
        }

        showNotification(error?.message, 'error')
      },
    },
  )
}
</script>

<style scoped>
.create-round-page {
  gap: 1.4rem;
  padding: 1.6rem 0 2rem;
}

.round-hero {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1.5rem;
}

.round-hero-copy {
  min-width: 0;
}

.breadcrumb-label {
  display: inline-flex;
  align-items: center;
  gap: 0.7rem;
  margin-bottom: 0.75rem;
  color: var(--accent-strong);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.round-hero h1 {
  margin: 0;
  max-width: 760px;
  color: var(--foreground);
  font-size: var(--text-4xl);
  line-height: var(--text-4xl--line-height);
  font-family: var(--font-display);
  font-weight: 800;
}

.section-subtitle {
  margin: 0.45rem 0 0;
  max-width: 780px;
  color: var(--muted-foreground);
  font-size: var(--text-base);
  line-height: var(--text-base--line-height);
}

.round-rule {
  height: 1px;
  margin: 0.7rem 0 0.9rem;
  background: var(--line-soft);
}

.round-form-card {
  width: 100%;
}

.round-form {
  gap: 0;
}

.form-section {
  padding: 0.5rem 0 2rem;
  border-bottom: 1px solid var(--line-soft);
}

.form-section + .form-section {
  padding-top: 2rem;
}

.form-section:last-of-type {
  padding-bottom: 1.5rem;
  border-bottom: 0;
}

.form-section-heading {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.4rem;
}

.form-section-heading h2 {
  margin: 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-size: var(--text-xl);
  line-height: var(--text-xl--line-height);
  font-weight: 800;
}

.form-section-heading p {
  margin: 0.3rem 0 0;
  color: var(--muted-foreground);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
}

.form-grid,
.schedule-grid,
.requirements-grid,
.evaluation-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 1.2rem;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
  min-width: 0;
}

.form-label {
  color: var(--foreground);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  font-weight: 700;
}

.datetime-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 140px;
  gap: 0.6rem;
  align-items: center;
}

.text-error {
  color: var(--destructive);
  font-size: var(--text-sm);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: 1.5rem;
}

.submit-btn {
  min-width: 150px;
}

@media (max-width: 760px) {
  .create-round-page {
    padding: 1rem 1rem 2rem;
  }

  .round-hero {
    align-items: stretch;
    flex-direction: column;
    gap: 1rem;
  }

  .round-hero h1 {
    font-size: var(--text-3xl);
    line-height: var(--text-3xl--line-height);
  }

  .section-subtitle {
    font-size: var(--text-sm);
    line-height: var(--text-sm--line-height);
  }

  .form-grid,
  .schedule-grid,
  .requirements-grid,
  .evaluation-grid {
    grid-template-columns: 1fr;
  }

  .form-section {
    padding-bottom: 1.5rem;
  }

  .form-section + .form-section {
    padding-top: 1.5rem;
  }

  .form-section-heading {
    gap: 0.7rem;
  }

  .form-actions {
    justify-content: stretch;
  }

  .submit-btn {
    width: 100%;
  }

  .datetime-row {
    grid-template-columns: 1fr;
  }
}
</style>
