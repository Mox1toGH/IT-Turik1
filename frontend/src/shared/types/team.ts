import type { UserRole } from './user'

export interface TeamMember {
  id: number
  username: string
  email: string
  full_name: string
  role: UserRole
  avatar?: string | null
}
