/**
 * Compatibility shim — re-exports from Orval-generated points API
 * with the legacy hook aliases used by existing Vue components.
 */
export {
  useGetMyPointsBalance as useMyPointsBalance,
  useListMyPointsTransactions as useMyPointsTransactions,
  useGetAdminUserPointsBalance as useAdminPointsBalance,
  useListAdminUserPointsTransactions as useAdminPointsTransactions,
  useModifyUserPointsBalance as useModifyUserPoints,
} from '@/api/points/points'
