<template>
  <ui-modal :model-value="props.modelValue" @update:model-value="toggleOpen">
    <template #title>
      <h3>Create event</h3>
    </template>

    <form class="add-form">
      <label class="form-item">
        <p class="form-label">Title</p>
        <ui-input
          v-model="form.fields.value.title"
          :is-invalid="!!form.errors.value.title"
          @blur="form.validateField('title')"
        />
        <small v-if="form.errors.value.title" class="text-error">{{
          form.errors.value.title
        }}</small>
      </label>

      <label class="form-item">
        <p class="form-label">Link</p>
        <ui-input
          v-model="form.fields.value.link"
          :is-invalid="!!form.errors.value.link"
          @blur="form.validateField('link')"
        />
        <small v-if="form.errors.value.link" class="text-error">{{ form.errors.value.link }}</small>
      </label>

      <label class="form-item">
        <p class="form-label">Start Date</p>
        <ui-date-picker
          v-model="form.fields.value.start_date"
          :is-invalid="!!form.errors.value.start_date"
          @blur="form.validateField('start_date')"
        />
        <small v-if="form.errors.value.start_date" class="text-error">{{
          form.errors.value.start_date
        }}</small>
      </label>

      <label class="form-item">
        <p class="form-label">Start Time</p>
        <ui-time-picker
          v-model="form.fields.value.start_time"
          :is-invalid="!!form.errors.value.start_time"
          @blur="form.validateField('start_time')"
        />
        <small v-if="form.errors.value.start_time" class="text-error">{{
          form.errors.value.start_time
        }}</small>
      </label>

      <label class="form-item">
        <p class="form-label">Description</p>
        <ui-text-area
          v-model="form.fields.value.description"
          :is-invalid="!!form.errors.value.description"
          @blur="form.validateField('description')"
        />
        <small v-if="form.errors.value.description" class="text-error">{{
          form.errors.value.description
        }}</small>
      </label>
    </form>

    <template #footer>
      <ui-button variant="secondary" @click="handleClose"> Close </ui-button>
      <ui-button @click="createEvent"> <loading-icon v-if="isPending" /> Save </ui-button>
    </template>
  </ui-modal>
</template>

<script setup lang="ts">
import UiDatePicker from '@/components/ui/UiDatePicker.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiModal from '@/components/ui/UiModal.vue'
import UiTimePicker from '@/components/ui/UiTimePicker.vue'
import UiButton from '@/components/ui/UiButton.vue'
import { useForm } from '@/composables/useForm'
import { AddEventSchema } from '@/schemas/tournaments.schema'
import UiTextArea from '@/components/ui/UiTextArea.vue'
import { useCreateEvent } from '@/api/queries/tournaments'
import { combineDateAndTime } from '@/lib/date'
import { useNotification } from '@/composables/useNotification'
import { parseApiError } from '@/api/errors'

interface Props {
  modelValue: boolean
  tournamentId: number
}

interface Form {
  title: string
  description: string
  link: string
  start_date: Date
  start_time: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
}>()

const form = useForm<Form>(AddEventSchema, {
  title: '',
  description: '',
  link: '',
  start_date: new Date(),
  start_time: '00:00',
})
const { showNotification } = useNotification()

const { mutate: create, isPending } = useCreateEvent()
const createEvent = () => {
  if (!form.validate()) return

  create(
    {
      body: {
        tournament: props.tournamentId,
        type: 'event',
        title: form.fields.value.title,
        description: form.fields.value.description,
        link: form.fields.value.link,
        start_datetime: combineDateAndTime(
          form.fields.value.start_date,
          form.fields.value.start_time,
        ),
      },
    },
    {
      onError: (error) => {
        const parsedError = parseApiError(error)
        showNotification(parsedError?.message, 'error')
      },

      onSuccess: () => {
        handleClose()
      },
    },
  )
}

function toggleOpen() {
  emit('update:modelValue', !props.modelValue)
}

function handleClose() {
  toggleOpen()
  form.reset()
}
</script>

<style scoped>
.add-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
</style>
