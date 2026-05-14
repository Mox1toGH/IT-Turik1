/**
 * Compatibility shim — re-exports from Orval-generated points API
 * with the legacy hook aliases used by existing Vue components.
 */
export {
  useGetMyPointsBalance as useMyPointsBalance,
  useListMyPointsTransactions as useMyPointsTransactions,
  useGetAdminUserPointsBalance as useAdminUserPointsBalance,
  useListAdminUserPointsTransactions as useAdminUserPointsTransactions,
  useModifyUserPointsBalance as useAdminModifyUserPoints,
} from '@/api/points/points'
