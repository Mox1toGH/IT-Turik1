<template>
  <form class="tournament-form" @submit.prevent="handleSubmit">
    <tournament-basics-fields :form="form" />
    <tournament-capacity-fields :form="form" />
    <tournament-schedule-fields :form="form" />

    <div class="form-actions">
      <ui-button type="submit" size="lg" :disabled="isPending">
        {{ isPending ? 'Creating...' : 'Create tournament' }}
      </ui-button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { useCreateTournament } from '@/api/tournaments/tournaments'
import UiButton from '@/components/ui/UiButton'
import { useForm } from '@/composables/useForm'
import { useNotification } from '@/composables/useNotification'
import { CreateTournamentSchema } from '@/schemas/tournaments.schema'
import { unref } from 'vue'
import { useRouter } from 'vue-router'
import TournamentBasicsFields from '../tournament-form/TournamentBasicsFields.vue'
import TournamentCapacityFields from '../tournament-form/TournamentCapacityFields.vue'
import TournamentScheduleFields from '../tournament-form/TournamentScheduleFields.vue'
import {
  createTournamentFormDefaults,
  toTournamentPayload,
  type TournamentFormFields,
} from '../../composables/useTournamentForm'

const form = useForm<TournamentFormFields>(
  CreateTournamentSchema as never,
  createTournamentFormDefaults(),
)

const router = useRouter()
const { mutate: createTournament, isPending } = useCreateTournament()
const { showNotification } = useNotification()

const handleSubmit = () => {
  const values = unref(form.fields)

  if (!form.validate()) return

  createTournament(
    {
      data: toTournamentPayload(values),
    },
    {
      onSuccess() {
        router.push('/tournaments')
      },

      onError: (error) => {
        for (const [field, message] of Object.entries(error.details ?? {})) {
          form.setError(field, message)
        }

        showNotification(error.message, 'error')
      },
    },
  )
}
</script>

<style scoped>
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
</style>
