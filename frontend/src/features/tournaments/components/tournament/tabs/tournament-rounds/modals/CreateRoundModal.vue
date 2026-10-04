<template>
  <ui-modal v-model="isOpen" max-width="960px" @close="handleClose" scrollable>
    <template #title>
      <h2>Create round</h2>
    </template>

    <form id="round-form" class="round-form" @submit.prevent="handleSubmit">
      <div class="form-section">
        <div class="form-section-heading">
          <span class="step-marker">01</span>
          <div>
            <h3>Round details</h3>
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
            <h3>Schedule</h3>
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
            <h3>Requirements</h3>
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
            <h3>Evaluation</h3>
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
            <add-criteria-modal
              v-model="form.fields.value.criteria"
              @blur="form.validateField('criteria')"
            />
            <small v-if="form.errors.value.criteria" class="text-error">
              {{ form.errors.value.criteria }}
            </small>
          </label>
        </div>
      </div>
    </form>

    <template #footer>
      <ui-button variant="secondary" @click="isOpen = false">Cancel</ui-button>
      <ui-button type="submit" form="round-form" :disabled="isPending">
        <loading-icon v-if="isPending" />
        <span>Create round</span>
      </ui-button>
    </template>
  </ui-modal>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton.vue'
import UiModal from '@/components/ui/UiModal.vue'
import UiDatePicker from '@/components/ui/UiDatePicker.vue'
import UiNumberInput from '@/components/ui/UiNumberInput.vue'
import UiInput from '@/components/ui/UiInput.vue'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import AddCriteriaModal from './AddCriteriaModal.vue'
import EditorModal from './EditorModal.vue'
import { useForm } from '@/composables/useForm'
import { CreateRoundSchema } from '@/schemas/tournaments.schema'
import type { JSONContent } from '@tiptap/core'
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
  tech_requirements?: JSONContent
  description?: JSONContent
  must_have_requirements?: JSONContent
  criteria: RoundCriteriaItem[]
  start_date: Date
  start_time: string
  end_date: Date
  end_time: string
}

const props = defineProps<{
  tournamentId: number
}>()

const isOpen = defineModel<boolean>({ required: true })

const { showNotification } = useNotification()

const form = useForm<Form>(CreateRoundSchema, {
  name: '',
  passing_count: 2,
  description: undefined,
  tech_requirements: undefined,
  must_have_requirements: undefined,
  criteria: [],
  start_date: new Date(),
  start_time: '00:00',
  end_date: new Date(),
  end_time: '23:59',
})

const { mutate: createRound, isPending } = useCreateRound()

function handleClose() {
  isOpen.value = false
}

function handleSubmit() {
  if (!form.validate()) return

  const { start_time, end_time, ...rest } = form.fields.value

  createRound(
    {
      tournamentPk: props.tournamentId,
      data: {
        ...rest,
        start_date: combineDateAndTime(form.fields.value.start_date, start_time).toISOString(),
        end_date: combineDateAndTime(form.fields.value.end_date, end_time).toISOString(),
      },
    },
    {
      onSuccess: () => {
        isOpen.value = false
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
.round-form {
  display: flex;
  flex-direction: column;
  padding-right: 0.25rem;
}

.form-section {
  padding: 1.5rem 0 2rem;
  border-bottom: 1px solid var(--line-soft);
}

.form-section:last-of-type {
  padding-bottom: 1rem;
  border-bottom: 0;
}

.form-section-heading {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.4rem;
}

.form-section-heading h3 {
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

@media (max-width: 760px) {
  .form-grid,
  .schedule-grid,
  .requirements-grid,
  .evaluation-grid,
  .datetime-row {
    grid-template-columns: 1fr;
  }

  .form-section-heading {
    gap: 0.7rem;
  }
}
</style>
