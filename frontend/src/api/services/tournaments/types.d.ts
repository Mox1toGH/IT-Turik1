import type {
  EventId,
  Round,
  RoundId,
  Submission,
  SubmissionId,
  Team,
  TeamId,
  Tournament,
  TournamentEvent,
  TournamentId,
  TournamentStatus,
  User,
} from '@/api/dbTypes'
import type { MaybeRefOrGetter } from 'vue'

// Get tournaments
export interface GetTournamentsArgs {
  page: number
  pageSize?: number
  searchQuery?: string
  status?: Exclude<TournamentStatus, 'draft'>[]
}

export interface GetTournamentsResponse {
  data: (Pick<
    Tournament,
    | 'id'
    | 'name'
    | 'description'
    | 'start_date'
    | 'end_date'
    | 'max_teams'
    | 'min_team_members'
    | 'status'
    | 'banner'
  > & { rounds: Pick<Round, 'id' | 'name' | 'start_date' | 'end_date' | 'status'> })[]
  total: number
}

// Get tournaments
export interface GetTournamentsArgs {
  page: number
  pageSize?: number
  searchQuery?: string
  status: TournamentStatus
}

// Create tournament
export type CreateTournamentBody = Pick<
  Tournament,
  'name' | 'description' | 'start_date' | 'end_date' | 'max_teams' | 'min_team_members'
>

export interface CreateTournamentArgs {
  body: CreateTournamentBody
}

// Tournament info
export interface GetTournamentInfoArgs {
  id: TournamentId
}

export type GetTournamentInfoResponse = Tournament & {
  rounds: Pick<Round, 'id' | 'name' | 'start_date' | 'end_date' | 'status'>[]
  registered_team: Pick<Team, 'id' | 'name'> | null
}

// Get active team tournament
export interface GetActiveTeamTournamentArgs {
  id: TeamId
}

export type GetActiveTeamTournamentResponse = Pick<
  Tournament,
  'id' | 'name' | 'status' | 'start_date'
>

// Get registered teams
export interface GetRegisteredTeamsArgs {
  id: TournamentId
  includeInactive?: boolean
  status?: 'active' | 'disqualified' | 'all'
}

export type GetRegisteredTeamsResponse = (Pick<Team, 'id' | 'name' | 'is_public'> & {
  registration_id: number
  members_count: number
  is_active: boolean
  is_disqualified: boolean
  members: Pick<User, 'id' | 'username' | 'email' | 'full_name' | 'role'>[]
  disqualification_reason: string
})[]

// Tournament rounds
export interface GetRoundsArgs {
  id: TournamentId
}

export type GetRoundsResponse = Round[]

// Get eligible teams
export interface GetEligibleTeamsArgs {
  id: TournamentId
}

export type GetEligibleTeamsResponse = (Pick<Team, 'id' | 'name'> & {
  members_count: number
})[]

// Create round
export type CreateRoundBody = Pick<
  Round,
  | 'name'
  | 'passing_count'
  | 'description'
  | 'tech_requirements'
  | 'must_have_requirements'
  | 'criteria'
  | 'start_date'
  | 'end_date'
> & {
  tournament: TournamentId
}

export interface CreateRoundArgs {
  id: TournamentId
  body: CreateRoundBody
}

// delete round
export interface DeleteRoundArgs {
  id: RoundId
}

// edit round
export interface EditRoundArgs {
  id: RoundId
  body: EditRoundBody
}

export type EditRoundBody = Pick<
  Round,
  | 'name'
  | 'passing_count'
  | 'description'
  | 'tech_requirements'
  | 'must_have_requirements'
  | 'criteria'
  | 'start_date'
  | 'end_date'
>

export type EditRoundResponse = Round

// Get current round
export interface GetCurrentRoundArgs {
  id: TournamentId
}

export type GetCurrentRoundResponse = Pick<
  Round,
  'id' | 'name' | 'must_have_requirements' | 'tech_requirements'
> & {
  tournament_id: TournamentId
  tournamnet_name: Pick<Tournament, 'name'>
  task: Pick<Round, 'description'>
  deadline: string
}

// Register team

export interface RegisterTeamBody {
  team_id: TeamId
}

export interface RegisterTeamArgs {
  id: TournamentId
  body: RegisterTeamBody
}

// Leave team from tournament
export interface LeaveTeamBody {
  team_id: TeamId
}

export interface LeaveTeamArgs {
  id: TournamentId
  body: LeaveTeamBody
}

// Submit round

export interface SubmitRoundBody {
  round: RoundId
  github_url: string
  demo_video_url: string
  description: string
}

export interface SubmitRoundArgs {
  body: SubmitRoundBody
}

// create Event
export type CreateEventBody = Pick<
  TournamentEvent,
  'title' | 'description' | 'start_datetime' | 'tournament' | 'type' | 'link'
>

export interface CreateEventArgs {
  body: CreateEventBody
}

// get events
export interface GetEventsArgs {
  tournamentId: TournamentId
}

export type GetEventsResponse = TournamentEvent[]

// Edit event
export type EditEventBody = Pick<TournamentEvent, 'title' | 'start_datetime' | 'description' | 'type' | 'link'>

export interface EditEventArgs {
  eventId: EventId
  body: EditEventBody
}

// delete event
export interface DeleteEventArgs {
  eventId: EventId
}

// my calendar
export interface GetMyCalendarResponse {
  events: TournamentEvent[]
  rounds: Round[]
}

// start registration
export interface StartRegistrationArgs {
  tournamentId: TournamentId
}

// start registration
export interface StartRoundArgs {
  roundId: RoundId
}

export type StartRoundResponse = Round

// close submissions
export interface CloseSubmissionsArgs {
  roundId: RoundId
}

export type CloseSubmissionsResponse = Round

// mark evaluated
export interface MarkEvaluatedArgs {
  roundId: RoundId
}

export type MarkEvaluatedResponse = Round

// tournament submissions
export interface GetTeamSubmissionsArgs {
  tournamentId: TournamentId
}

export type GetTeamSubmissionsResponse = (Submission & {
  team_details: Pick<Team, 'id' | 'name' | 'is_public'>
  round_details: Pick<Round, 'id' | 'name' | 'start_date' | 'end_date' | 'status'>
  assignments: {
    id: number
    jury: {
      id: number
      username: string
      full_name: string
      role: string
    }
    evaluation: {
      id: number
      scores: { criterion_id: string; criterion_name?: string; score: number }[]
      total_score: number
      final_score: number
      comment: string
      created_at: string
    } | null
    created_at: string
  }[]
})[]

// edit submission
export interface EditSubmissionArgs {
  submissionId: SubmissionId
  body: EditSubmissionBody
}

export interface EditSubmissionBody {
  github_url: string
  demo_video_url: string
  description: string
}

export type EditSubmissionResponse = Submission & {
  team_details: Pick<Team, 'id' | 'name' | 'is_public'>
  round_details: Pick<Round, 'id' | 'name' | 'start_date' | 'end_date' | 'status'>
}

// round submissions
export interface GetRoundSubmissionsArgs {
  roundId: MaybeRefOrGetter<RoundId>
}

export type GetRoundSubmissionsResponse = GetTeamSubmissionsResponse

// Update registration
export interface UpdateRegistrationArgs {
  tournamentId: TournamentId
  registrationId: number
  body: {
    action: 'disqualify' | 'reactivate'
    disqualification_reason?: string
  }
}

export interface UpdateRegistrationResponse {
  id: number
  is_active: boolean
  disqualification_reason: string | null
  action: 'activated' | 'disqualified'
}

// tournament banner
export interface UpdateTournamentBannerArgs {
  tournamentId: TournamentId
  file: File
}

// Tournament archive
export interface GetTournamentArchiveListArgs {}

export type TournamentArchiveStanding = {
  rank: number
  team: Pick<Team, 'id' | 'name' | 'is_public'>
  total_score: number
  average_score: number
  criteria_breakdown: Record<string, number>
  jury_breakdown: Record<string, number> | null
  rounds_breakdown: unknown[] | null
  snapshot_at: string
}

export type TournamentArchiveItem = Pick<
  Tournament,
  'id' | 'name' | 'description' | 'start_date' | 'end_date' | 'status' | 'banner'
> & {
  teams: Pick<Team, 'id' | 'name' | 'is_public'>[]
  standings: TournamentArchiveStanding[]
}

export type GetTournamentArchiveListResponse = TournamentArchiveItem[]

export interface GetTournamentArchiveDetailArgs {
  id: TournamentId
}

export type GetTournamentArchiveDetailResponse = TournamentArchiveItem & {
  rounds: Pick<Round, 'id' | 'name' | 'start_date' | 'end_date' | 'status'>[]
}

export interface GetTournamentArchiveSubmissionsArgs {
  id: TournamentId
}

export type GetTournamentArchiveSubmissionsResponse = GetTeamSubmissionsResponse
