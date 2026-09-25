import type { ProductResponse } from '@/api/backendAPINinja.schemas'

export const getProductImage = (product: ProductResponse): string =>
  product.images?.[0]?.image || product.avatar_frame?.svg_file || product.digital_asset_url || ''
