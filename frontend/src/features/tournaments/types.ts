import type { JSONContent } from '@tiptap/vue-3'
import type { TeamMember } from '@/shared/types/team'

export type TournamentStatus = 'draft' | 'registration' | 'running' | 'finished'
export type RoundStatus = 'draft' | 'active' | 'submission_closed' | 'evaluated'

export interface Criterion {
  id: string
  name: string
  description: string
  max_score: number
}

export interface Round {
  id: number
  tournament: number
  name: string
  description: JSONContent
  tech_requirements: JSONContent
  must_have_requirements: JSONContent
  criteria: Criterion[]
  start_date: string
  end_date: string
  passing_count?: number | null
  evaluation_criteria: string
  materials: unknown[]
  status: RoundStatus
}

export interface TournamentTeam {
  id: number
  registration_id: number
  name: string
  members_count: number
  members: TeamMember[]
  is_public: boolean
  is_active: boolean
  is_disqualified: boolean
  disqualification_reason?: string | null
}

export interface Tournament {
  id: number
  name: string
  description: string
  start_date: string
  end_date: string
  max_teams?: number | null
  min_team_members?: number | null
  banner?: string | null
  status: TournamentStatus
  rounds: Array<Pick<Round, 'id' | 'name' | 'start_date' | 'end_date' | 'status'>>
  registered_team?: { id: number; name: string; is_public: boolean } | null
}

export interface TournamentArchive {
  id: number
  name: string
  description: string
  start_date: string
  end_date: string
  status: TournamentStatus
  banner?: string | null
  standings: ArchiveStanding[]
  teams?: Array<{ id: number; name: string; is_public: boolean }>
  rounds?: Array<Pick<Round, 'id' | 'name' | 'start_date' | 'end_date' | 'criteria'>>
}

export interface ArchiveStanding {
  rank: number
  team: { id: number; name: string; is_public: boolean }
  total_score: number
}

export interface ArchiveSubmission {
  id: number
  round_details: { id: number; name: string }
  team_details: { id: number; name: string; is_public: boolean }
  description: string
  github_url: string
  demo_video_url: string
  live_demo_url: string
  assignments: Array<{
    id: number
    jury: { id: number; username: string; full_name: string }
    evaluation?: {
      final_score: number
      total_score: number
      comment: string
      scores: Array<{ criterion_id: string; criterion_name: string; score: number }>
    } | null
  }>
}

export interface TournamentLeaderboardEntry {
  team_id: number
  team_name: string
  total_score: number
  rank: number
  rounds: Array<{
    round_id: number
    round_name: string
    total_score: number
    average_score: number
    jury_breakdown?: Record<string, number> | null
  }>
}

export interface TournamentListFilters {
  page?: number
  page_size?: number
  searchQuery?: string | null
  status?: string | null
}
