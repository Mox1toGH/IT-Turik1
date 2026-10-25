import { computed, ref, watch, type ComputedRef, type Ref } from 'vue'

export type EvaluationStatusFilter = 'all' | 'evaluated' | 'not_evaluated'

export interface EvaluationFilterOption {
  value: string
  label: string
}

interface RoundDetailsLike {
  id: number | string
  name?: string | null
  tournament?: number | null
}

interface AssignmentLike {
  round_details: RoundDetailsLike
  is_evaluated: boolean
}

interface TournamentRoundLike {
  id: number | string
  name?: string | null
}

interface TournamentLike {
  id: number | string
  name: string
  rounds?: TournamentRoundLike[] | null
}

export interface EvaluationFilters<TAssignment extends AssignmentLike = AssignmentLike> {
  selectedRounds: Ref<string[]>
  selectedTournamentIds: Ref<string[]>
  evaluationStatus: Ref<EvaluationStatusFilter>
  currentPage: Ref<number>
  pageSize: number
  roundOptions: ComputedRef<EvaluationFilterOption[]>
  tournamentOptions: ComputedRef<EvaluationFilterOption[]>
  filteredAssignments: ComputedRef<TAssignment[]>
  pagedAssignments: ComputedRef<TAssignment[]>
  totalCount: ComputedRef<number>
  evaluatedCount: ComputedRef<number>
  progressPercent: ComputedRef<number>
}

export const EVALUATION_STATUS_OPTIONS: EvaluationFilterOption[] = [
  { value: 'all', label: 'All evaluations' },
  { value: 'evaluated', label: 'Evaluated' },
  { value: 'not_evaluated', label: 'Not evaluated' },
]

export function useEvaluationFilters<
  TAssignment extends AssignmentLike,
  TTournament extends TournamentLike,
>(
  assignments: Ref<TAssignment[]>,
  tournaments: Ref<TTournament[]>,
  pageSize = 10,
): EvaluationFilters<TAssignment> {
  const selectedRounds = ref<string[]>([])
  const selectedTournamentIds = ref<string[]>([])
  const evaluationStatus = ref<EvaluationStatusFilter>('all')
  const currentPage = ref<number>(1)

  const roundOptions = computed<EvaluationFilterOption[]>(() => {
    const unique = new Map<string, string>()

    assignments.value.forEach((assignment) => {
      unique.set(
        String(assignment.round_details.id),
        assignment.round_details.name ?? `Round #${assignment.round_details.id}`,
      )
    })

    tournaments.value.forEach((tournament) => {
      const rounds = Array.isArray(tournament.rounds) ? tournament.rounds : []
      rounds.forEach((round) => {
        unique.set(String(round.id), round.name ?? `Round #${round.id}`)
      })
    })

    return Array.from(unique.entries()).map(([value, label]) => ({ value, label }))
  })

  const tournamentOptions = computed<EvaluationFilterOption[]>(() => {
    const byId = new Map<string, string>()

    tournaments.value.forEach((tournament) => {
      byId.set(String(tournament.id), tournament.name)
    })

    assignments.value.forEach((assignment) => {
      const id = assignment.round_details.tournament
      if (id == null) return
      const key = String(id)
      if (!byId.has(key)) byId.set(key, `Tournament #${key}`)
    })

    return Array.from(byId.entries()).map(([value, label]) => ({ value, label }))
  })

  const filteredAssignments = computed<TAssignment[]>(() => {
    let list = assignments.value

    if (selectedRounds.value.length) {
      list = list.filter((assignment) =>
        selectedRounds.value.includes(String(assignment.round_details.id)),
      )
    }

    if (selectedTournamentIds.value.length) {
      list = list.filter((assignment) =>
        selectedTournamentIds.value.includes(String(assignment.round_details.tournament)),
      )
    }

    if (evaluationStatus.value === 'evaluated') {
      list = list.filter((assignment) => assignment.is_evaluated)
    } else if (evaluationStatus.value === 'not_evaluated') {
      list = list.filter((assignment) => !assignment.is_evaluated)
    }

    return list
  })

  const pagedAssignments = computed<TAssignment[]>(() => {
    const start = (currentPage.value - 1) * pageSize
    const end = start + pageSize
    return filteredAssignments.value.slice(start, end)
  })

  const totalCount = computed<number>(() => filteredAssignments.value.length)
  const evaluatedCount = computed<number>(
    () => filteredAssignments.value.filter((item) => item.is_evaluated).length,
  )
  const progressPercent = computed<number>(() =>
    totalCount.value ? Math.round((evaluatedCount.value / totalCount.value) * 100) : 0,
  )

  watch([selectedRounds, selectedTournamentIds, evaluationStatus], () => {
    currentPage.value = 1
  })

  return {
    selectedRounds,
    selectedTournamentIds,
    evaluationStatus,
    currentPage,
    pageSize,
    roundOptions,
    tournamentOptions,
    filteredAssignments,
    pagedAssignments,
    totalCount,
    evaluatedCount,
    progressPercent,
  }
}
