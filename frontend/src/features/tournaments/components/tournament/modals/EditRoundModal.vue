<template>
  <ui-modal
    :model-value="props.modelValue"
    @update:model-value="toggleOpen"
    @close="toggleClose"
    max-width="1200px"
    scrollable
  >
    <template #title>
      <h2>Edit round</h2>
    </template>

    <form class="round-form" @submit.prevent="handleSubmit">
      <label class="form-item title-field">
        <span class="form-label">Name</span>
        <ui-input
          v-model="form.fields.value.name"
          placeholder="Enter round title"
          :isInvalid="!!form.errors.value.name"
          @blur="form.validateField('name')"
        />
        <small v-if="form.errors.value.name" class="text-error">{{ form.errors.value.name }}</small>
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
        <small v-if="form.errors.value.description" class="text-error">{{
          form.errors.value.description
        }}</small>
      </label>

      <label class="form-item tech-field">
        <span class="form-label">Technical requirements</span>
        <editor-modal
          v-model="form.fields.value.tech_requirements"
          title="Technical requirements"
          addText="Add technical requirements"
          editText="Edit technical requirements"
          ariaLabel="Technical requirements editor"
          @blur="form.validateField('tech_requirements')"
        />
        <small v-if="form.errors.value.tech_requirements" class="text-error">{{
          form.errors.value.tech_requirements
        }}</small>
      </label>

      <label class="form-item start-date-field">
        <span class="form-label">Start date</span>
        <ui-date-picker
          v-model="form.fields.value.start_date"
          :isInvalid="!!form.errors.value.start_date"
          @blur="form.validateField('start_date')"
        />
        <small v-if="form.errors.value.start_date" class="text-error">{{
          form.errors.value.start_date
        }}</small>
      </label>

      <label class="form-item start-time-field">
        <span class="form-label">Start time</span>
        <ui-input
          v-model="form.fields.value.start_time"
          type="time"
          :isInvalid="!!form.errors.value.start_time"
          @blur="form.validateField('start_time')"
        />
        <small v-if="form.errors.value.start_time" class="text-error">{{
          form.errors.value.start_time
        }}</small>
      </label>

      <label class="form-item end-date-field">
        <span class="form-label">End date</span>
        <ui-date-picker
          v-model="form.fields.value.end_date"
          :isInvalid="!!form.errors.value.end_date"
          @blur="form.validateField('end_date')"
        />
        <small v-if="form.errors.value.end_date" class="text-error">{{
          form.errors.value.end_date
        }}</small>
      </label>

      <label class="form-item end-time-field">
        <span class="form-label">End time</span>
        <ui-input
          v-model="form.fields.value.end_time"
          type="time"
          :isInvalid="!!form.errors.value.end_time"
          @blur="form.validateField('end_time')"
        />
        <small v-if="form.errors.value.end_time" class="text-error">{{
          form.errors.value.end_time
        }}</small>
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

      <label class="form-item must-have-field">
        <span class="form-label">Must have</span>
        <editor-modal
          v-model="form.fields.value.must_have_requirements"
          title="Must have"
          addText="Add must have"
          editText="Edit must have"
          ariaLabel="Must have editor"
          @blur="form.validateField('must_have_requirements')"
        />
        <small v-if="form.errors.value.must_have_requirements" class="text-error">{{
          form.errors.value.must_have_requirements
        }}</small>
      </label>

      <label class="form-item passing-count-field">
        <span class="form-label">Passing count</span>
        <ui-input
          type="number"
          v-model.number="form.fields.value.passing_count"
          placeholder="Enter passing teams count"
          :isInvalid="!!form.errors.value.passing_count"
          @blur="form.validateField('passing_count')"
        />
        <small v-if="form.errors.value.passing_count" class="text-error">{{
          form.errors.value.passing_count
        }}</small>
      </label>

      <ui-button class="submit-btn" type="submit" :disabled="isPending">
        <loading-icon v-if="isPending" />
        <p>Edit</p></ui-button
      >
    </form>
  </ui-modal>
</template>

<script setup lang="ts">
import UiDatePicker from '@/components/ui/UiDatePicker.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiModal from '@/components/ui/UiModal.vue'
import { useForm } from '@/composables/useForm'
import { EditRoundSchema } from '@/schemas/tournaments.schema'
import { type JSONContent } from '@tiptap/vue-3'
import AddCriteriaModal from '../../create-round/modals/AddCriteriaModal.vue'
import UiButton from '@/components/ui/UiButton.vue'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import EditorModal from '../../create-round/modals/EditorModal.vue'
import { parseApiError } from '@/api/errors'
import { useEditRound } from '@/api/queries/tournaments'
import type { Round } from '@/api/dbTypes'
import { useNotification } from '@/composables/useNotification'
import { combineDateAndTime } from '@/lib/date'
import EditorModal from '@/components/shared/EditorModal.vue'
import type { Criterion, Round } from '@/api/.ts.schemas'
import { useUpdateRound } from '@/api/tournaments/tournaments'

interface Props {
  modelValue: boolean
  round: Round
}

interface Form {
  name: string
  passing_count: number
  tech_requirements: JSONContent | null
  description: JSONContent | null
  must_have_requirements: JSONContent | null
  criteria: Criterion[]
  start_date: Date
  start_time: string
  end_date: Date
  end_time: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
}>()

const { showNotification } = useNotification()
const pad = (value: number) => String(value).padStart(2, '0')
const startDate = new Date(props.round.start_date)
const endDate = new Date(props.round.end_date)

const form = useForm<Form>(EditRoundSchema, {
  name: props.round.name ?? '',
  passing_count: props.round.passing_count ?? 1,
  description: props.round.description ?? '',
  tech_requirements: props.round.tech_requirements ?? {},
  must_have_requirements: props.round.must_have_requirements ?? {},
  criteria: props.round.criteria,
  start_date: startDate,
  start_time: `${pad(startDate.getHours())}:${pad(startDate.getMinutes())}`,
  end_date: endDate,
  end_time: `${pad(endDate.getHours())}:${pad(endDate.getMinutes())}`,
})

const { mutate: editRound, isPending } = useUpdateRound()

function handleSubmit() {
  if (!form.validate()) return
  const { start_time, end_time, ...rest } = form.fields.value

  editRound(
    {
      id: props.round.id,
      data: {
        ...rest,
        start_date: combineDateAndTime(form.fields.value.start_date, start_time),
        end_date: combineDateAndTime(form.fields.value.end_date, end_time),
      },
    },
    {
      onSuccess: () => {
        emit('update:modelValue', false)
        showNotification('Successfully changed round info', 'success')
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

const toggleOpen = () => {
  emit('update:modelValue', !props.modelValue)
}

const toggleClose = () => {
  toggleOpen()
  form.reset()
}
</script>

<style scoped>
.round-form {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto auto auto;
  gap: 1rem;
}

.title-field {
  grid-column: 1;
  grid-row: 1;
}

.desc-field {
  grid-column: 1;
  grid-row: 2;
}

.tech-field {
  grid-column: 1;
  grid-row: 3;
}

.must-have-field {
  grid-column: 2;
  grid-row: 5;
}

.start-date-field {
  grid-column: 2;
  grid-row: 1;
}

.end-date-field {
  grid-column: 2;
  grid-row: 2;
}

.start-time-field {
  grid-column: 2;
  grid-row: 3;
}

.end-time-field {
  grid-column: 2;
  grid-row: 4;
}

.passing-count-field {
  grid-column: 1;
  grid-row: 6;
}

.criteria-field {
  grid-column: 2;
  grid-row: 6;
}

.submit-btn {
  grid-column: 2;
  grid-row: 7;
}

.text-error {
  color: var(--destructive);
}

@media (max-width: 800px) {
  .round-form {
    grid-template-columns: 1fr;
    grid-template-rows: auto;
    gap: 1.2rem;
  }

  .must-have-field {
    grid-column: 1;
    grid-row: 4;
  }

  .passing-count-field {
    grid-row: 5;
  }

  .start-date-field,
  .start-time-field,
  .end-date-field,
  .end-time-field,
  .criteria-field,
  .submit-btn {
    grid-column: 1;
    grid-row: auto;
  }
}
</style>
