import { describe, it, expect } from 'vitest'
import { QueryClient } from '@tanstack/query-core'
import { invalidationKeys } from './queryClient'
import {
  getGetTournamentTeamRegistrationQueryKey,
  getListMyTeamSubmissionsQueryKey,
  getListRoundSubmissionsQueryKey,
  getListRoundsQueryKey,
  getListTournamentSubmissionsQueryKey,
  getListTournamentTeamsQueryKey,
} from '@/api/tournaments/tournaments'
import {
  getGetRoundPassingStatusQueryKey,
  getGetTournamentLeaderboardQueryKey,
  getListAvailableJuryQueryKey,
} from '@/api/evaluation/evaluation'
import { getGetTeamQueryKey, getListTeamsQueryKey } from '@/api/teams/teams'
import { getGetNewsQueryKey, getListNewsQueryKey } from '@/api/news/news'

/** True when invalidating with `filter` marks the query registered under `key`. */
const invalidates = (filter: readonly unknown[] | undefined, key: readonly unknown[]): boolean => {
  if (!filter) return false
  const scoped = new QueryClient()
  scoped.setQueryData(key, [])
  scoped.invalidateQueries({ queryKey: filter })
  const query = scoped.getQueryCache().getAll()[0]
  return !!query && query.state.isInvalidated
}

describe('invalidationKeys', () => {
  it('targets the keys the tournament submission tab reads', () => {
    // updateSubmission only receives the submission id; the tournament comes back
    // in the response body.
    const keys = invalidationKeys('updateSubmission', { id: 7 }, {
      round: 26,
      round_details: { tournament: 106 },
    })

    expect(invalidates(keys[2], getListMyTeamSubmissionsQueryKey(106))).toBe(true)
    expect(invalidates(keys[3], getListRoundSubmissionsQueryKey(26))).toBe(true)
  })

  it('still reaches the submission lists when the payload carries no ids', () => {
    const keys = invalidationKeys('createSubmission', { data: { round: 26 } }, null)

    expect(invalidates(keys[1], getListMyTeamSubmissionsQueryKey(106))).toBe(true)
    expect(invalidates(keys[2], getListRoundSubmissionsQueryKey(26))).toBe(true)
    expect(invalidates(keys[3], getListTournamentSubmissionsQueryKey(106))).toBe(true)
  })

  it('uses the round id the jury assignment mutation really passes', () => {
    const keys = invalidationKeys('assignJuryToRound', { roundId: 26, data: [] }, null)

    expect(invalidates(keys[1], getListAvailableJuryQueryKey(26))).toBe(true)
    expect(invalidates(keys[2], getGetRoundPassingStatusQueryKey(26))).toBe(true)
    expect(invalidates(keys[3], getListRoundSubmissionsQueryKey(26))).toBe(true)
  })

  it('uses the team id the team mutations really pass', () => {
    const keys = invalidationKeys('removeMemberFromTeam', { pk: 4, userId: 9 }, null)

    expect(invalidates(keys[0], getGetTeamQueryKey(4))).toBe(true)
    expect(invalidates(invalidationKeys('teamBannerUpdate', { pk: 4 }, null)[1], getGetTeamQueryKey(4))).toBe(
      true,
    )
    expect(invalidates(invalidationKeys('deleteTeam', { pk: 4 }, null)[0], getListTeamsQueryKey())).toBe(
      true,
    )
  })

  it('reaches tournament scoped lists that only expose a round id', () => {
    const keys = invalidationKeys('deleteRound', { id: 26 }, null)

    expect(invalidates(keys[0], getListRoundsQueryKey(106))).toBe(true)
    expect(invalidates(keys[0], getListTournamentTeamsQueryKey(106))).toBe(true)
  })

  it('reaches nested keys when the parent id is known', () => {
    const keys = invalidationKeys('disqualifyTeamFromTournament', { id: 106 }, null)

    expect(invalidates(keys[1], getGetTournamentTeamRegistrationQueryKey(106, 3))).toBe(true)
  })

  it('never emits a key with an unknown path slot', () => {
    const samples: [string, unknown, unknown][] = [
      ['createSubmission', { data: {} }, null],
      ['createRound', { tournamentPk: 106, data: {} }, null],
      ['markRoundEvaluated', { id: 26 }, { tournament: 106 }],
      ['assignJuryToRound', { roundId: 26 }, null],
      ['updateSubmission', { id: 7 }, {}],
      ['deleteRound', { id: 26 }, null],
    ]

    for (const [mutationKey, vars, data] of samples) {
      for (const key of invalidationKeys(mutationKey, vars, data)) {
        expect(key, `${mutationKey} emitted a key with a hole`).not.toContain(undefined)
        expect(key, `${mutationKey} emitted a key with a hole`).not.toContain(null)
      }
    }
  })

  it('keeps the news detail key aligned with the article id the mutation passes', () => {
    const keys = invalidationKeys('updateNews', { articleId: 12, data: {} }, null)

    expect(invalidates(keys[0], getListNewsQueryKey())).toBe(true)
    expect(invalidates(keys[1], getGetNewsQueryKey(12))).toBe(true)
  })

  it('only invalidates the leaderboard of the scored tournament', () => {
    const keys = invalidationKeys('markRoundEvaluated', { id: 26 }, { tournament: 106 })

    expect(invalidates(keys[4], getGetTournamentLeaderboardQueryKey(106))).toBe(true)
    expect(invalidates(keys[4], getGetTournamentLeaderboardQueryKey(999))).toBe(false)
  })
})
