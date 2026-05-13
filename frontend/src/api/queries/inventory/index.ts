import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import type { AxiosError } from 'axios'

import { $api } from '@/api/services'
import { inventoryKeys } from '@/api/queries/keys'
import type { QueryConfig } from '@/api/queries/types'
import type { ApiError } from '@/api/errors'
import type { UserInventoryItem, InventoryPaginated } from '@/api/services/inventory/types'

export const useMyInventory = (
  config?: QueryConfig<InventoryPaginated<UserInventoryItem>>,
) => {
  return useQuery<InventoryPaginated<UserInventoryItem>, AxiosError<ApiError>>({
    queryKey: inventoryKeys.my(),
    queryFn: () => $api.inventory.getMyInventory(),
    ...config,
  })
}

export const useEquipInventoryItem = () => {
  const queryClient = useQueryClient()
  return useMutation<UserInventoryItem, AxiosError<ApiError>, { inventoryId: number }>({
    mutationFn: ({ inventoryId }) => $api.inventory.equipItem(inventoryId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: inventoryKeys.myPrefix() })
      queryClient.invalidateQueries({ queryKey: ['accounts', 'profile'] })
      queryClient.invalidateQueries({ queryKey: ['accounts', 'users'] })
    },
  })
}

export const useUnequipInventoryItem = () => {
  const queryClient = useQueryClient()
  return useMutation<UserInventoryItem, AxiosError<ApiError>, { inventoryId: number }>({
    mutationFn: ({ inventoryId }) => $api.inventory.unequipItem(inventoryId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: inventoryKeys.myPrefix() })
      queryClient.invalidateQueries({ queryKey: ['accounts', 'profile'] })
      queryClient.invalidateQueries({ queryKey: ['accounts', 'users'] })
    },
  })
}
