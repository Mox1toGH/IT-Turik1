import { apiClient } from '@/api/client'
import type { UserInventoryItem, InventoryPaginated } from './types'

const prefix = '/api/inventory'

export const inventoryService = {
  async getMyInventory() {
    const { data } = await apiClient.get<InventoryPaginated<UserInventoryItem>>(`${prefix}/my/`, {
      params: { page_size: 100 },
    })
    return data
  },

  async equipItem(inventoryId: number) {
    const { data } = await apiClient.post<UserInventoryItem>(`${prefix}/equip/`, {
      inventory_id: inventoryId,
    })
    return data
  },

  async unequipItem(inventoryId: number) {
    const { data } = await apiClient.post<UserInventoryItem>(`${prefix}/unequip/`, {
      inventory_id: inventoryId,
    })
    return data
  },
}
