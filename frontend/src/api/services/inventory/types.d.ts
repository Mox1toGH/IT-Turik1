import type { ShopProduct } from '../shop/types'

export interface UserInventoryItem {
  id: number
  product: ShopProduct
  is_equipped: boolean
  acquired_at: string
  updated_at: string
}

export interface InventoryPaginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}
