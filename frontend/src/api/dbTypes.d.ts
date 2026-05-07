// ── User ────────────────────────────────────────────────────
export type UserId = number
export type UserRole = 'admin' | 'team' | 'jury' | 'organizer'

export interface User {
  id: UserId
  username: string
  email: string
  role: 'admin' | 'team' | 'jury' | 'organizer'
  full_name?: string
  phone: string
  city?: string
  created_at: Date
  needs_onboarding: boolean
  teams: Pick<Team, 'id' | 'name' | 'contact_telegram' | 'contact_discord'>[]
}

// ── Role Activation Code ────────────────────────────────────────────────────
export type RoleActivationId = number

export interface RoleActivationCode {
  id: RoleActivationId
  code: string
  role: UserRole
  is_used: boolean
  created_by?: User
  created_at: Date
  used_by?: User
  used_at?: Date
}

// ── Team ────────────────────────────────────────────────────
export type TeamId = number

export interface Team {
  id: TeamId
  name: string
  email: string
  members: Pick<User, 'id' | 'username' | 'email' | 'full_name' | 'role'>[]
  invitations: Invitation[]
  join_requests: JoinRequest[]
  is_public: boolean
  organization: string
  contact_telegram: string
  contact_discord: string
}

// ── Invatation ────────────────────────────────────────────────────
type InvitationId = number
type InvatitionStatus = 'invited' | 'accepted' | 'declined'

interface Invitation {
  id: InvatationId
  status: InvatationStatus
  team: Pick<Team, 'id' | 'name' | 'is_public'>
  user: Pick<User, 'id' | 'username' | 'email' | 'full_name' | 'role'>
  invited_by: Pick<User, 'id' | 'username' | 'email' | 'full_name' | 'role'>
  created_at: Date
  updated_at?: Date
  responded_at?: Date
}

// ── Join Request ────────────────────────────────────────────────────
type JoinRequestId = number
type JoinRequestStatus = 'pending' | 'accepted' | 'declined'

interface JoinRequest {
  id: JoinRequestId
  status: JoinRequestStatus
  team: Team
  user: Pick<User, 'id' | 'username' | 'email' | 'full_name' | 'role'>
  reviewed_by?: User
  reviewed_at?: Date
  created_at: Date
  updated_at: Date
}

// Tournament
type TournamentId = number
type TournamentStatus = 'draft' | 'registration' | 'running' | 'finished'

interface Tournament {
  id: TournamentId
  name: string
  description: string
  start_date: Date
  end_date: Date
  max_teams: number
  min_team_members: number
  rounds_count: number
  status: TournamentStatus
}

// Round
type RoundId = number
type RoundStatus = 'draft' | 'active' | 'submission_closed' | 'evaluated'

interface CriteriaItem {
  id: string
  name: string
  description: string
  max_score: number
}

type EvaluationCriteria = 'score'

interface Round {
  id: RoundId
  name: string
  start_date: Date
  end_date: Date
  status: RoundStatus
  description: JSONContent
  must_have_requirements: JSONContent
  tech_requirements: JSONContent
  passing_count: number
  winners_count: number
  evaluation_criteria
  criteria: CriteriaItem[]
}

// Event

type EventId = number

interface TournamentEvent {
  description: string
  icon: 2
  id: EventId
  link: string
  start_datetime: Date
  title: string
  tournament: TournamentId
  type: 'event' // TODO: remove cuz we dont need this
  created_at: Date
  updated_at: Date
}
