<template>
  <ui-modal :model-value="props.modelValue" @update:model-value="toggleOpen" @close="form.reset()">
    <template #title>
      <h3>Edit event</h3>
    </template>

    <form class="edit-form">
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
        <p class="form-label">Start Date</p>
        <ui-date-picker
          v-model="form.fields.value.startDate"
          :is-invalid="!!form.errors.value.startDate"
          @blur="form.validateField('startDate')"
        />
        <small v-if="form.errors.value.startDate" class="text-error">{{
          form.errors.value.startDate
        }}</small>
      </label>

      <label class="form-item">
        <p class="form-label">Start Time</p>
        <ui-time-picker
          v-model="form.fields.value.startTime"
          :is-invalid="!!form.errors.value.startTime"
          @blur="form.validateField('startTime')"
        />
        <small v-if="form.errors.value.startTime" class="text-error">{{
          form.errors.value.startTime
        }}</small>
      </label>
    </form>

    <template #footer>
      <ui-button variant="secondary" @click="toggleClose"> Close </ui-button>
      <ui-button @click="editEvent"> <loading-icon v-if="isPending" /> Save </ui-button>
    </template>
  </ui-modal>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton.vue'
import UiDatePicker from '@/components/ui/UiDatePicker.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiModal from '@/components/ui/UiModal.vue'
import UiTimePicker from '@/components/ui/UiTimePicker.vue'
import { useEditEvent } from '@/api/queries/tournaments'
import { useForm } from '@/composables/useForm'
import { EditEventSchema } from '@/schemas/tournaments.schema'
import { parseApiError } from '@/api/errors'
import { useNotification } from '@/composables/useNotification'
import { combineDateAndTime } from '@/lib/date'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import { useQueryClient } from '@tanstack/vue-query'
import type { TournamentId } from '@/api/dbTypes'
import { touranmentsKeys } from '@/api/queries/keys'

interface Props {
  modelValue: boolean
  eventId: number
  tournamentId: TournamentId
  title: string
  startDate: Date | string
}

interface Form {
  title: string
  startDate: Date
  startTime: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
}>()

const { showNotification } = useNotification()
const queryClient = useQueryClient()

const date = props.startDate instanceof Date ? props.startDate : new Date(props.startDate)
const pad = (value: number) => String(value).padStart(2, '0')
const form = useForm<Form>(EditEventSchema, {
  title: props.title,
  startDate: date,
  startTime: `${pad(date.getHours())}:${pad(date.getMinutes())}`,
})

const { mutate, isPending } = useEditEvent()
const editEvent = () => {
  mutate(
    {
      eventId: props.eventId,
      body: {
        title: form.fields.value.title,
        start_datetime: combineDateAndTime(
          form.fields.value.startDate,
          form.fields.value.startTime,
        ),
      },
    },
    {
      onError: (err) => {
        const parsedError = parseApiError(err)
        for (const [field, errors] of Object.entries(parsedError?.details || {})) {
          form.setError(field as keyof Form, errors?.[0] ?? 'Invalid value')
        }

        showNotification(parsedError?.message, 'error')
      },
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: touranmentsKeys.events(props.tournamentId) })
        emit('update:modelValue', false)
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
.edit-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
</style>
