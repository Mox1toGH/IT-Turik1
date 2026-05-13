export type ShopProductType = 'physical' | 'digital'
export type ShopOrderStatus = 'pending' | 'confirmed' | 'shipped' | 'completed' | 'cancelled'
export type ShopProductOrdering = 'name' | '-name' | 'price' | '-price'

export interface ShopPaginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface ShopCategory {
  id: number
  name: string
}

export interface ShopProductImage {
  id: number
  image: string
  created_at: string
}

export interface ShopProduct {
  id: number
  name: string
  description: string
  price: number
  stock_quantity: number
  category: ShopCategory
  product_type: ShopProductType
  digital_asset_url?: string
  images: ShopProductImage[]
  is_active: boolean
  is_available: boolean
  created_at: string
  updated_at: string
}

export interface DigitalInventoryItem {
  id: number
  product: ShopProduct
  is_equipped: boolean
  acquired_at: string
  updated_at: string
}

export interface ShopUserRef {
  id: number
  username: string
  email: string
  full_name: string
}

export interface ShopOrder {
  id: number
  user: ShopUserRef
  user_profile_url: string
  product: ShopProduct
  quantity: number
  total_cost: number
  status: ShopOrderStatus
  created_at: string
  updated_at: string
}

export interface GetProductsArgs {
  page?: number
  pageSize?: number
  search?: string
  category?: number | null
  productType?: ShopProductType | 'all'
  ordering?: ShopProductOrdering
}

export interface PurchaseBody {
  product_id: number
  quantity: number
}

export interface UpdateOrderStatusBody {
  status: Exclude<ShopOrderStatus, 'cancelled'>
}

export interface UpsertProductBody {
  name: string
  description: string
  price: number
  stock_quantity: number
  category_id: number
  product_type: ShopProductType
  digital_asset_url?: string
  is_active: boolean
  uploaded_images?: File[]
}

export interface UpsertCategoryBody {
  name: string
}
