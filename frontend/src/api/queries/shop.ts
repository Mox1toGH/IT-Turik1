/**
 * Compatibility shim — re-exports from Orval-generated shop API
 * with the legacy hook aliases used by existing Vue components.
 */
export {
  useListProducts as useShopProducts,
  useListAdminCategories as useAdminShopCategories,
  useCreateAdminCategory,
  useUpdateAdminCategory,
  useDeleteAdminCategory,
  useListAvatarFrames as useAvatarFrames,
  useCreateAdminProduct,
  useUpdateAdminProduct,
  useDeleteAdminProduct,
  usePurchaseProduct as useShopPurchase,
  useListMyOrders as useMyShopOrders,
  useCancelMyOrder as useCancelMyShopOrder,
  useListAdminOrders as useAdminShopOrders,
  useCancelAdminOrder,
  useUpdateAdminOrderStatus,
} from '@/api/shop/shop'
