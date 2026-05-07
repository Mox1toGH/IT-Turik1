import type {
  EventId,
  Round,
  RoundId,
  Team,
  TeamId,
  Tournament,
  TournamentEvent,
  TournamentId,
  TournamentStatus,
} from '@/api/dbTypes'

// Get tournaments
export interface GetTournamentsArgs {
  page: number
  pageSize?: number
  searchQuery?: string
  status?: Exclude<TournamentStatus, 'draft'>[]
}

export interface GetTournamentsResponse {
  // TODO: add rounds type annotation
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
  > & { rounds: [] })[]
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
  | 'name'
  | 'description'
  | 'start_date'
  | 'end_date'
  | 'rounds_count'
  | 'max_teams'
  | 'min_team_members'
>

export interface CreateTournamentArgs {
  body: CreateTournamentBody
}

// Tournament info
export interface GetTournamentInfoArgs {
  id: TournamentId
}

export type GetTournamentInfoResponse = Tournament & {
  rounds: [] // TODO
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
}

export type GetRegisteredTeamsResponse = (Pick<Team, 'id' | 'name' | 'is_public'> & {
  members_count: number
  is_active: boolean
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

// Submit round

export interface SubmitRoundBody {
  team: TeamId
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
  'title' | 'description' | 'link' | 'start_datetime' | 'tournament'
> & {
  type: 'event' // TODO: remove this. We dont actually need to pass type of event
}

export interface CreateEventArgs {
  body: CreateEventBody
}

// get events
export interface GetEventsArgs {
  tournamentId: TournamentId
}

export type GetEventsResponse = TournamentEvent[]

// Edit event
export type EditEventBody = Pick<TournamentEvent, 'title' | 'start_datetime'>

export interface EditEventArgs {
  eventId: EventId
  body: EditEventBody
}

// delete event
export interface DeleteEventArgs {
  eventId: EventId
}
