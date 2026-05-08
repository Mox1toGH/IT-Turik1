import type { RoundId, SubmissionId, User, UserId } from '@/api/dbTypes'
import type { MaybeRefOrGetter } from 'vue'

// available jury
export interface GetAvailableJuryArgs {
  roundId: MaybeRefOrGetter<RoundId>
}

export type GetAvailableJuryResponse = Pick<User, 'id' | 'username' | 'full_name' | 'email'>[]

// assign jury
export interface AssignJuryArgs {
  roundId: RoundId
  body: AssignJuryBody
}

export type AssignJuryBody = {
  submission: SubmissionId
  jury: UserId[]
}[]
