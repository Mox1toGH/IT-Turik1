<template>
  <ui-modal :model-value="modelValue" @update:model-value="toggleOpen">
    <template #title>
      <h3>Submit round</h3>
    </template>

    <form class="submit-form">
      <label class="form-item">
        <p class="form-label">Github url</p>
        <ui-input
          v-model="form.fields.value.github_url"
          :is-invalid="!!form.errors.value.github_url"
          @blur="form.validateField('github_url')"
        />
        <small v-if="form.errors.value.github_url" class="text-error">{{
          form.errors.value.github_url
        }}</small>
      </label>

      <label class="form-item">
        <p class="form-label">Demo url</p>
        <ui-input
          v-model="form.fields.value.demo_video_url"
          :is-invalid="!!form.errors.value.demo_video_url"
          @blur="form.validateField('demo_video_url')"
        />
        <small v-if="form.errors.value.demo_video_url" class="text-error">{{
          form.errors.value.demo_video_url
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
      <ui-button variant="secondary" @click="toggleClose"> Close </ui-button>
      <ui-button @click="submitRound"> <loading-icon v-if="isPending" /> Submit </ui-button>
    </template>
  </ui-modal>
</template>

<script setup lang="ts">
import type { RoundId, TournamentId } from '@/api/dbTypes'
import { parseApiError } from '@/api/errors'
import { useSubmitRound } from '@/api/queries/tournaments'
import UiButton from '@/components/ui/UiButton.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiModal from '@/components/ui/UiModal.vue'
import UiTextArea from '@/components/ui/UiTextArea.vue'
import { useForm } from '@/composables/useForm'
import { useNotification } from '@/composables/useNotification'
import { SubmitRoundSchema } from '@/schemas/tournaments.schema'

interface Props {
  modelValue: boolean
  roundId: RoundId
  tournamentId: TournamentId
}

interface Form {
  github_url: string
  demo_video_url: string
  description: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
}>()
const { showNotification } = useNotification()

const form = useForm<Form>(SubmitRoundSchema, {
  github_url: '',
  demo_video_url: '',
  description: '',
})

const { mutate: submit, isPending } = useSubmitRound()
const submitRound = () => {
  if (!form.validate()) return

  submit(
    {
      body: {
        team: 0, // TODO: get from active tournament team
        round: props.roundId,
        ...form.fields.value,
      },
    },
    {
      onError: (error) => {
        const parsedError = parseApiError(error)
        for (const [field, errors] of Object.entries(parsedError?.details || {})) {
          form.setError(field as keyof Form, errors?.[0] ?? 'Invalid value')
        }

        showNotification(parsedError?.message, 'error')
      },

      onSuccess() {
        showNotification('Success', 'success')
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
.submit-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
</style>
