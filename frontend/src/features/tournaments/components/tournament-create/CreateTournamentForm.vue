<template>
  <div class="create-layout">
    <form class="tournament-form" @submit.prevent="handleSubmit">
      <tournament-basics-fields :form="form" />
      <tournament-capacity-fields :form="form" />
      <tournament-schedule-fields :form="form" />

      <ui-card class="form-actions">
        <ui-button asLink to="/tournaments" variant="secondary" size="lg">Cancel</ui-button>
        <ui-button type="submit" size="lg" :disabled="isPending">
          {{ isPending ? 'Creating...' : 'Create tournament' }}
        </ui-button>
      </ui-card>
    </form>

    <tournament-summary-aside
      :name="form.fields.value.name"
      :description="form.fields.value.description"
      :max-teams="form.fields.value.max_teams"
      :min-team-members="form.fields.value.min_team_members"
      :starts-label="startsLabel"
      :ends-label="endsLabel"
    />
  </div>
</template>

<script setup lang="ts">
import { useCreateTournament } from '@/api/tournaments/tournaments'
import UiButton from '@/components/ui/UiButton'
import UiCard from '@/components/ui/UiCard'
import { useForm } from '@/composables/useForm'
import { useNotification } from '@/composables/useNotification'
import { combineDateAndTime, formatDate } from '@/lib/date'
import { CreateTournamentSchema } from '@/schemas/tournaments.schema'
import { computed, unref } from 'vue'
import { useRouter } from 'vue-router'
import TournamentBasicsFields from '../tournament-form/TournamentBasicsFields.vue'
import TournamentCapacityFields from '../tournament-form/TournamentCapacityFields.vue'
import TournamentScheduleFields from '../tournament-form/TournamentScheduleFields.vue'
import TournamentSummaryAside from '../tournament-form/TournamentSummaryAside.vue'
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

const startsLabel = computed(() =>
  formatDate(combineDateAndTime(form.fields.value.startDate, form.fields.value.startTime), {
    showHours: true,
  }),
)

const endsLabel = computed(() =>
  formatDate(combineDateAndTime(form.fields.value.endDate, form.fields.value.endTime), {
    showHours: true,
  }),
)

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

.form-actions {
  display: flex;
  flex-direction: row;
  justify-content: end;
  gap: 0.75rem;
}

@media (max-width: 980px) {
  .create-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .form-actions {
    position: static;
    flex-direction: column-reverse;
  }
}
</style>
