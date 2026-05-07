import type { TeamId, TournamentId, UserId } from '@/api/dbTypes'

export interface CertificateItem {
  id: number
  unique_code: string
  user: UserId | null
  full_name: string
  team: TeamId | null
  team_name: string | null
  tournament: TournamentId | null
  tournament_name: string | null
  placement: string
  certificate_number: string
  template: number | null
  template_name: string | null
  certificate_url: string
  created_at: string
}

export type GetCertificatesResponse = CertificateItem[]
