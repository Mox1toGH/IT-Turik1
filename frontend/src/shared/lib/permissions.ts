import type { UserRole, UserSummary } from '@/shared/types/user'

type RoleBearingUser = Pick<UserSummary, 'role'> | null | undefined

/** Shared role checks for application-wide permissions. */
export function hasRole(user: RoleBearingUser, role: UserRole): boolean {
  return user?.role === role
}

export function hasAnyRole(user: RoleBearingUser, roles: readonly UserRole[]): boolean {
  return roles.some((role) => hasRole(user, role))
}
