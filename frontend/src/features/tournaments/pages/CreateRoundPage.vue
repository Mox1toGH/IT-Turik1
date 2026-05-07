<template>
  <ui-card>
    <template #header>
      <h1>Create round</h1>
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
        <p>Create</p></ui-button
      >
    </form>
  </ui-card>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiDatePicker from '@/components/ui/UiDatePicker.vue'
import UiInput from '@/components/ui/UiInput.vue'
import AddCriteriaModal from '../components/create-round/modals/AddCriteriaModal.vue'
import EditorModal from '../components/create-round/modals/EditorModal.vue'
import { useForm } from '@/composables/useForm'
import { CreateRoundSchema } from '@/schemas/tournaments.schema'
import type { JSONContent } from '@tiptap/core'
import { useCreateRound } from '@/api/queries/tournaments'
import { useRoute, useRouter } from 'vue-router'
import { parseApiError } from '@/api/errors'
import { useNotification } from '@/composables/useNotification'

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
  end_date: Date
}

const form = useForm<Form>(CreateRoundSchema, {
  name: '',
  passing_count: 2,
  description: null,
  tech_requirements: null,
  must_have_requirements: null,
  criteria: [],
  start_date: new Date(),
  end_date: new Date(),
})

const route = useRoute()
const router = useRouter()
const { showNotification } = useNotification()
const tournamentId = Number(route.params.id)

const { mutate: createRound, isPending } = useCreateRound()

function handleSubmit() {
  if (!form.validate()) return

  createRound(
    {
      id: tournamentId,
      body: {
        tournament: tournamentId,
        ...form.fields.value,
      },
    },
    {
      onSuccess: () => {
        router.push({
          path: '/tournaments/5',
          query: {
            section: 'rounds',
          },
        })
      },
      onError(error) {
        const parsedError = parseApiError(error)
        for (const [field, errors] of Object.entries(parsedError?.details || {})) {
          form.setError(field as keyof Form, errors?.[0] ?? 'Invalid value')
        }
        showNotification(parsedError?.message, 'error')
      },
    },
  )
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
  grid-row: 3;
}

.start-date-field {
  grid-column: 2;
  grid-row: 1;
}

.end-date-field {
  grid-column: 2;
  grid-row: 2;
}

.passing-count-field {
  grid-column: 1;
  grid-row: 5;
}

.criteria-field {
  grid-column: 2;
  grid-row: 5;
}

.submit-btn {
  grid-column: 2;
  grid-row: 6;
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
  .end-date-field,
  .criteria-field,
  .submit-btn {
    grid-column: 1;
    grid-row: auto;
  }
}
</style>
