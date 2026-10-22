import { computed, reactive, ref, toValue, watch, type MaybeRefOrGetter } from 'vue'
import { useNotification } from '@/composables/useNotification'
import { useGetTournament, useListRoundSubmissions } from '@/api/tournaments/tournaments'
import {
  useAssignJuryToRound,
  useListAvailableJury,
  type AssignJuryToRoundMutationBody,
} from '@/api/evaluation/evaluation'
import type { SelectOption } from '@/components/ui/UiSelect'

export function useJuryAssign(tournamentId: MaybeRefOrGetter<number>) {
  const id = computed<number>(() => toValue(tournamentId))
  const { showNotification } = useNotification()

  const tournamentQuery = useGetTournament(id)
  const {
    data: tournament,
    isLoading: tournamentLoading,
    error: tournamentErrorData,
  } = tournamentQuery

  const closedRound = computed(() =>
    tournament.value?.rounds.find((round) => round.status === 'submission_closed'),
  )

  const submissionsQuery = useListRoundSubmissions(
    computed(() => closedRound.value?.id ?? 0),
    undefined,
    {
      query: { enabled: computed(() => !!closedRound.value) },
    },
  )
  const {
    data: submissions,
    isLoading: submissionsLoading,
    error: submissionsErrorData,
  } = submissionsQuery

  const {
    data: availableJury,
    isLoading: isFetchingJury,
    isError: isFailedToFetchJury,
    error: juryFetchError,
  } = useListAvailableJury(
    computed(() => closedRound.value?.id ?? 0),
    undefined,
    {
      query: { enabled: computed(() => !!closedRound.value) },
    },
  )

  const submissionItems = computed(() => submissions.value?.items ?? [])
  const juryItems = computed(() => availableJury.value?.items ?? [])

  const noClosedRound = computed<boolean>(() => !!tournament.value && !closedRound.value)
  const isLoading = computed<boolean>(() => tournamentLoading.value || submissionsLoading.value)
  const isFetching = computed<boolean>(
    () => tournamentQuery.isFetching.value || submissionsQuery.isFetching.value,
  )
  const refetchAll = (): void => {
    void tournamentQuery.refetch()
    void submissionsQuery.refetch()
  }
  // A disabled query stays `pending` forever, so only the round that is actually
  // being fetched may keep the card in its loading state; "no closed round yet" is
  // an empty state, not a failure.
  const cardQuery = computed(() => ({
    isPending:
      tournamentQuery.isPending.value || (!!closedRound.value && submissionsQuery.isPending.value),
    isError: tournamentQuery.isError.value || submissionsQuery.isError.value,
    data: noClosedRound.value ? [] : submissionItems.value,
    error: tournamentErrorData.value ?? submissionsErrorData.value ?? null,
    isFetching: isFetching.value,
    refetch: refetchAll,
  }))
  const juryOptions = computed<SelectOption[]>(
    () =>
      juryItems.value.map((jury) => ({
        value: jury.id,
        label: jury.username,
      })) ?? [],
  )

  const assignJuryForAll = ref<number[]>([])
  const assignedJury = reactive<Record<number, number[]>>({})
  watch(
    submissionItems,
    (value) => {
      if (!value.length) return
      value.forEach((submission) => {
        const nextAssigned = (submission.assignments ?? [])
          .map((assignment) => assignment.jury?.id)
          .filter((id): id is number => typeof id === 'number')

        assignedJury[submission.id] = Array.from(new Set(nextAssigned))
      })
    },
    { immediate: true },
  )

  const { mutate: assign, isPending } = useAssignJuryToRound()

  const applyJuryToAllSubmissions = (): void => {
    if (!submissionItems.value.length) return
    const nextAssigned = Array.from(new Set(assignJuryForAll.value))
    submissionItems.value.forEach((submission) => {
      assignedJury[submission.id] = [...nextAssigned]
    })
  }

  const handleAssignJury = (): void => {
    if (!closedRound.value) return
    const payload = submissionItems.value.map((submission) => {
      return {
        submission: submission.id,
        jury: assignedJury[submission.id],
      }
    })

    assign(
      {
        roundId: closedRound.value?.id,
        data: payload as unknown as AssignJuryToRoundMutationBody,
      },
      {
        onError: (error) => {
          showNotification(error?.message, 'error')
        },
        onSuccess: () => {
          showNotification('Assigment was sucessfully replaced', 'success')
        },
      },
    )
  }

  const juryLabel = (value: number): string =>
    juryOptions.value.find((option) => option.value === value)?.label ?? String(value)

  const teamAbbr = (teamName: string): string =>
    teamName
      .split(' ')
      .map((word) => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 3)

  return {
    closedRound,
    submissions: submissionItems,
    noClosedRound,
    isLoading,
    cardQuery,
    isFetching,
    refetchAll,
    juryOptions,
    juryFetchError,
    isFetchingJury,
    isFailedToFetchJury,
    assignJuryForAll,
    assignedJury,
    isPending,
    applyJuryToAllSubmissions,
    handleAssignJury,
    juryLabel,
    teamAbbr,
  }
}

export type JuryAssignSubmission = NonNullable<
  ReturnType<typeof useJuryAssign>['submissions']['value']
>[number]
