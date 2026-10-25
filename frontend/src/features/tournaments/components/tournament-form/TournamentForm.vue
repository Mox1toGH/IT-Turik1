<template>
  <ui-query-block v-if="isEdit" :query="tournamentQuery" title="tournament">
    <ui-query-field>
      <template #skeleton>
        <div class="form-skeleton">
          <ui-skeleton variant="rect" height="220px" />
          <ui-skeleton variant="rect" height="140px" />
          <ui-skeleton variant="rect" height="200px" />
        </div>
      </template>
      <tournament-form-fields
        :form="form"
        :is-pending="isPending"
        :submit-text="submitText"
        :pending-text="pendingText"
        @submit="handleSubmit"
      />
    </ui-query-field>
  </ui-query-block>

  <tournament-form-fields
    v-else
    :form="form"
    :is-pending="isPending"
    :submit-text="submitText"
    :pending-text="pendingText"
    @submit="handleSubmit"
  />
</template>

<script setup lang="ts">
import { computed, unref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { UiQueryBlock, UiQueryField } from '@/components/query'
import UiSkeleton from '@/components/ui/UiSkeleton'
import { useNotification } from '@/composables/useNotification'
import { useForm } from '@/composables/useForm'
import { CreateTournamentSchema } from '@/schemas/tournaments.schema'
import {
  useCreateTournament,
  useGetTournament,
  useUpdateTournament,
} from '@/api/tournaments/tournaments'
import TournamentFormFields from './TournamentFormFields.vue'
import {
  createTournamentFormDefaults,
  toTime,
  toTournamentPayload,
  type TournamentFormFields as TournamentFormValues,
} from '../../composables/useTournamentForm'

const props = withDefaults(
  defineProps<{
    mode: 'create' | 'edit'
    tournamentId?: number
  }>(),
  { tournamentId: undefined },
)

const isEdit = computed(() => props.mode === 'edit')
const router = useRouter()
const { showNotification } = useNotification()
const form = useForm<TournamentFormValues>(
  CreateTournamentSchema as never,
  createTournamentFormDefaults(),
)

const tournamentQuery = useGetTournament(computed(() => props.tournamentId ?? 0), {
  query: { enabled: isEdit },
})
const { data: tournament } = tournamentQuery
const { mutate: createTournament, isPending: isCreating } = useCreateTournament()
const { mutate: updateTournament, isPending: isUpdating } = useUpdateTournament()

const isPending = computed(() => (isEdit.value ? isUpdating.value : isCreating.value))
const submitText = computed(() => (isEdit.value ? 'Save changes' : 'Create tournament'))
const pendingText = computed(() => (isEdit.value ? 'Saving...' : 'Creating...'))

watch(
  tournament,
  (value) => {
    if (!isEdit.value || !value) return
    form.hydrate({
      name: value.name,
      description: value.description,
      startDate: new Date(value.start_date),
      startTime: toTime(value.start_date),
      endDate: new Date(value.end_date),
      endTime: toTime(value.end_date),
      max_teams: value.max_teams ?? 2,
      min_team_members: value.min_team_members ?? 2,
    })
  },
  { immediate: true },
)

function handleSubmit() {
  const values = unref(form.fields)
  if (!form.validate()) return

  const data = toTournamentPayload(values)
  if (isEdit.value) {
    if (!props.tournamentId) return
    updateTournament(
      { id: props.tournamentId, data },
      {
        onSuccess() {
          showNotification('Tournament updated successfully.', 'success')
          void router.push(`/tournaments/${props.tournamentId}`)
        },
        onError(error) {
          for (const [field, messages] of Object.entries(error?.details ?? {})) {
            form.setError(field, Array.isArray(messages) ? messages[0] ?? 'Invalid value' : messages)
          }
          showNotification(error.message, 'error')
        },
      },
    )
    return
  }

  createTournament(
    { data },
    {
      onSuccess() {
        void router.push('/tournaments')
      },
      onError(error) {
        for (const [field, messages] of Object.entries(error?.details ?? {})) {
          form.setError(field, Array.isArray(messages) ? messages[0] ?? 'Invalid value' : messages)
        }
        showNotification(error.message, 'error')
      },
    },
  )
}
</script>

<style scoped>
.form-skeleton {
  display: grid;
  gap: 1.25rem;
  width: 100%;
}
</style>
