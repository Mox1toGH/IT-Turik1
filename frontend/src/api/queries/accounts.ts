/**
 * Compatibility shim — re-exports from Orval-generated accounts API
 * with the legacy hook aliases used by existing Vue components.
 */
export { useGetUserProfile as useProfile, useUpdateUserProfile, useDeleteUserProfile } from '@/api/accounts/accounts'
export type { User } from '@/api/.ts.schemas'
