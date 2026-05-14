/**
 * Compatibility shim — re-exports from Orval-generated shop API
 * with the legacy hook aliases used by existing Vue components.
 */
export {
  useListProducts as useShopProducts,
  useListAdminCategories as useAdminShopCategories,
  useCreateAdminCategory as useAdminCreateCategory,
  useUpdateAdminCategory as useAdminUpdateCategory,
  useDeleteAdminCategory as useAdminDeleteCategory,
  useListAvatarFrames as useAvatarFrames,
  useCreateAdminProduct as useAdminCreateProduct,
  useUpdateAdminProduct as useAdminUpdateProduct,
  useDeleteAdminProduct as useAdminDeleteProduct,
  usePurchaseProduct as useShopPurchase,
  useListMyOrders as useMyShopOrders,
  useCancelMyOrder as useCancelMyShopOrder,
  useListAdminOrders as useAdminShopOrders,
  useCancelAdminOrder as useAdminCancelOrder,
  useUpdateAdminOrderStatus as useAdminUpdateOrderStatus,
} from '@/api/shop/shop'

export type { Category as ShopCategory, Product as ShopProduct, AvatarFrame as ShopAvatarFrame } from '@/api/.ts.schemas'
