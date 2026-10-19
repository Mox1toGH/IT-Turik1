import type { TeamMember } from '@/shared/types/team'
export type { TeamMember } from '@/shared/types/team'

export interface Team {
  id: number
  name: string
  email: string
  captain_id: number
  is_public: boolean
  organization?: string
  contact_telegram?: string
  contact_discord?: string
  banner?: string | null
  members: TeamMember[]
  is_member: boolean
  can_request_to_join: boolean
  is_in_active_tournament: boolean
}

export interface TeamInvitation {
  id: number
  user: TeamMember
  status: string
  created_at: string
  responded_at?: string | null
  invited_by_id?: number | null
}
