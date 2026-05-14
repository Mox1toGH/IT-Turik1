/**
 * Compatibility shim — re-exports from Orval-generated points API
 * with the legacy hook aliases used by existing Vue components.
 */
export {
  useGetMyPointsBalance as useMyPointsBalance,
  useListMyPointsTransactions as useMyPointsTransactions,
  useGetAdminUserPointsBalance as useAdminPointsBalance,
  useGetAdminUserPointsBalance as useAdminUserPointsBalance,
  useListAdminUserPointsTransactions as useAdminPointsTransactions,
  useListAdminUserPointsTransactions as useAdminUserPointsTransactions,
  useModifyUserPointsBalance as useModifyUserPoints,
  useModifyUserPointsBalance as useAdminModifyUserPoints,
} from '@/api/points/points'
