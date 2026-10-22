<template>
  <ui-query-block :query="tournamentQuery" title="tournament">
    <ui-query-field>
      <template #skeleton>
        <div class="form-skeleton">
          <ui-skeleton variant="rect" height="220px" />
          <ui-skeleton variant="rect" height="140px" />
          <ui-skeleton variant="rect" height="200px" />
        </div>
      </template>
      <form class="tournament-form" @submit.prevent="handleSubmit">
        <tournament-basics-fields :form="form" />
        <tournament-capacity-fields :form="form" />
        <tournament-schedule-fields :form="form" />

        <div class="form-actions">
          <ui-button type="submit" size="lg" :disabled="isPending">
            {{ isPending ? 'Saving...' : 'Save changes' }}
          </ui-button>
        </div>
      </form>
    </ui-query-field>
  </ui-query-block>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton'
import { UiQueryBlock, UiQueryField } from '@/components/query'
import UiSkeleton from '@/components/ui/UiSkeleton'
import { useForm } from '@/composables/useForm'
import { EditTournamentSchema } from '@/schemas/tournaments.schema'
import { unref, watch } from 'vue'
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

const tournamentQuery = useGetTournament(props.tournamentId)
const { data: tournament } = tournamentQuery

const { mutate: editTournament, isPending } = useUpdateTournament()

function toPayload(values: TournamentFormFields): UpdateTournamentMutationBody {
  return toTournamentPayload(values)
}

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

.form-skeleton {
  display: grid;
  gap: 1.25rem;
  width: 100%;
}
</style>
