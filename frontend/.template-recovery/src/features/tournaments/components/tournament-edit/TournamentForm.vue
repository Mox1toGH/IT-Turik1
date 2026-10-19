<template>
  <div v-if="isError" class="error-state">
    <ui-card>
      <p>Error while fetching tournament</p>
    </ui-card>
  </div>

  <ui-skeleton-loader v-else :loading="isLoading || isFetching">
    <template #skeleton>
      <div class="create-layout">
        <div class="tournament-form">
          <ui-skeleton variant="rect" height="220px" />
          <ui-skeleton variant="rect" height="140px" />
          <ui-skeleton variant="rect" height="200px" />
        </div>
        <ui-skeleton variant="rect" height="320px" />
      </div>
    </template>

    <div class="create-layout">
      <form class="tournament-form" @submit.prevent="handleSubmit">
        <tournament-basics-fields :form="form" />
        <tournament-capacity-fields :form="form" />
        <tournament-schedule-fields :form="form" />

        <ui-card class="form-actions">
          <ui-button asLink :to="`/tournaments/${tournamentId}`" variant="secondary" size="lg">
            Cancel
          </ui-button>
          <ui-button type="submit" size="lg" :disabled="isPending">
            {{ isPending ? 'Saving...' : 'Save changes' }}
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
        truncate-description
      />
    </div>
  </ui-skeleton-loader>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton'
import UiCard from '@/components/ui/UiCard'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader'
import UiSkeleton from '@/components/ui/UiSkeleton'
import { useForm } from '@/composables/useForm'
import { combineDateAndTime } from '@/lib/date'
import { EditTournamentSchema } from '@/schemas/tournaments.schema'
import { computed, unref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useNotification } from '@/composables/useNotification'
import {
  useGetTournament,
  useUpdateTournament,
  type UpdateTournamentMutationBody,
} from '@/api/tournaments/tournaments'
import TournamentBasicsFields from '../tournament-form/TournamentBasicsFields.vue'
import TournamentCapacityFields from '../tournament-form/TournamentCapacityFields.vue'
import TournamentScheduleFields from '../tournament-form/TournamentScheduleFields.vue'
import TournamentSummaryAside from '../tournament-form/TournamentSummaryAside.vue'
import {
  createTournamentFormDefaults,
  toTime,
  toTournamentPayload,
  type TournamentFormFields,
} from '../../composables/useTournamentForm'

const props = defineProps<{
  tournamentId: number
}>()

const router = useRouter()
const { showNotification } = useNotification()

const form = useForm<TournamentFormFields>(EditTournamentSchema, createTournamentFormDefaults())

const { data: tournament, isLoading, isFetching, isError } = useGetTournament(props.tournamentId)

const { mutate: editTournament, isPending } = useUpdateTournament()

function toPayload(values: TournamentFormFields): UpdateTournamentMutationBody {
  return toTournamentPayload(values)
}

const dateTimeFormatter = new Intl.DateTimeFormat(undefined, {
  dateStyle: 'medium',
  timeStyle: 'short',
})

function formatDateTime(date: Date, time: string) {
  try {
    const value = combineDateAndTime(date, time)
    return Number.isNaN(value.getTime()) ? '—' : dateTimeFormatter.format(value)
  } catch {
    return '—'
  }
}

const startsLabel = computed(() =>
  formatDateTime(form.fields.value.startDate, form.fields.value.startTime),
)
const endsLabel = computed(() =>
  formatDateTime(form.fields.value.endDate, form.fields.value.endTime),
)

watch(
  tournament,
  (value) => {
    if (!value) return

    form.fields.value = {
      name: value.name,
      description: value.description,
      startDate: new Date(value.start_date),
      startTime: toTime(value.start_date),
      endDate: new Date(value.end_date),
      endTime: toTime(value.end_date),
      max_teams: value.max_teams ?? 2,
      min_team_members: value.min_team_members ?? 2,
    }
  },
  { immediate: true },
)

const handleSubmit = () => {
  const values = unref(form.fields)

  if (!form.validate()) return

  editTournament(
    { id: props.tournamentId, data: toPayload(values) },
    {
      onSuccess() {
        showNotification('Tournament updated successfully.', 'success')
        router.push(`/tournaments/${props.tournamentId}`)
      },
      onError: (error) => {
        for (const [field, message] of Object.entries(error?.details || {})) {
          form.setError(field, message)
        }

        showNotification(error.message, 'error')
      },
    },
  )
}
</script>

<style scoped>
.error-state {
  display: flex;
  justify-content: center;
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

.form-actions {
  position: sticky;
  bottom: 1rem;
  display: flex;
  justify-content: flex-end;
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