export type UserRole = 'admin' | 'team' | 'jury' | 'organizer'

export interface UserSummary {
  id?: number
  username?: string
  email?: string
  role?: UserRole
  full_name?: string
  phone?: string
  city?: string
  is_staff?: boolean
  needs_onboarding?: boolean
  avatar?: string | null
  teams?: Array<Pick<UserTeam, 'id' | 'name'>>
  active_tournament?: UserActiveTournament | null
}

export interface User {
  id: number
  username: string
  email: string
  role: UserRole
  full_name: string
  phone: string
  city: string
  is_staff: boolean
  created_at: string
  needs_onboarding: boolean
  avatar?: string | null
  teams: UserTeam[]
  active_tournament: UserActiveTournament | null
}

export interface UserTeam {
  id: number
  name: string
  contact_telegram: string
  contact_discord: string
}

export interface UserActiveTournament {
  id: number
  name: string
  start_date: string
  end_date: string
  status: string
  team_registration_status: string
  team: { id: number; name: string }
  current_round: {
    id: number
    name: string
    status: string
    start_date: string
    end_date: string
  } | null
}
