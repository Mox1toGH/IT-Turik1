import type { Product } from '@/api/.ts.schemas'

export const getProductImage = (product: Product): string =>
  product.images?.[0]?.image || product.avatar_frame?.svg_file || product.digital_asset_url || ''
