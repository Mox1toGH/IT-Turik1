import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { computed, toValue, type MaybeRefOrGetter } from 'vue'
import type { AxiosError } from 'axios'

import { $api } from '@/api/services'
import { shopKeys } from '@/api/queries/keys'
import type { QueryConfig } from '@/api/queries/types'
import type { ApiError } from '@/api/errors'
import type {
  ShopCategory,
  ShopOrder,
  DigitalInventoryItem,
  ShopPaginated,
  ShopProduct,
  UpdateOrderStatusBody,
  UpsertCategoryBody,
  UpsertProductBody,
} from '@/api/services/shop/types'

export const useShopProducts = (
  args: {
    page?: MaybeRefOrGetter<number>
    pageSize?: MaybeRefOrGetter<number>
    search?: MaybeRefOrGetter<string>
    category?: MaybeRefOrGetter<number | null>
    productType?: MaybeRefOrGetter<'physical' | 'digital' | 'all'>
    ordering?: MaybeRefOrGetter<'name' | '-name' | 'price' | '-price'>
  } = {},
  config?: QueryConfig<ShopPaginated<ShopProduct>>,
) => {
  return useQuery<ShopPaginated<ShopProduct>, AxiosError<ApiError>>({
    queryKey: computed(() =>
      shopKeys.products({
        page: toValue(args.page) ?? 1,
        pageSize: toValue(args.pageSize) ?? 20,
        search: toValue(args.search) ?? '',
        category: toValue(args.category) ?? null,
        productType: toValue(args.productType) ?? 'all',
        ordering: toValue(args.ordering) ?? 'name',
      }),
    ),
    queryFn: () =>
      $api.shop.getProducts({
        page: toValue(args.page) ?? 1,
        pageSize: toValue(args.pageSize) ?? 20,
        search: toValue(args.search) ?? '',
        category: toValue(args.category) ?? null,
        productType: toValue(args.productType) ?? 'all',
        ordering: toValue(args.ordering) ?? 'name',
      }),
    ...config,
  })
}

export const useShopPurchase = () => {
  const queryClient = useQueryClient()
  return useMutation<ShopOrder, AxiosError<ApiError>, { productId: number; quantity: number }>({
    mutationFn: ({ productId, quantity }) =>
      $api.shop.purchase({ product_id: productId, quantity }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: shopKeys.productsPrefix() })
      queryClient.invalidateQueries({ queryKey: shopKeys.myOrdersPrefix() })
      queryClient.invalidateQueries({ queryKey: ['points', 'my-balance'] })
      queryClient.invalidateQueries({ queryKey: ['points', 'my-transactions'] })
    },
  })
}

export const useMyShopOrders = (
  args: { page?: MaybeRefOrGetter<number>; pageSize?: MaybeRefOrGetter<number> } = {},
  config?: QueryConfig<ShopPaginated<ShopOrder>>,
) => {
  return useQuery<ShopPaginated<ShopOrder>, AxiosError<ApiError>>({
    queryKey: computed(() =>
      shopKeys.myOrders({
        page: toValue(args.page) ?? 1,
        pageSize: toValue(args.pageSize) ?? 20,
      }),
    ),
    queryFn: () =>
      $api.shop.getMyOrders({
        page: toValue(args.page) ?? 1,
        pageSize: toValue(args.pageSize) ?? 20,
      }),
    ...config,
  })
}

export const useCancelMyShopOrder = () => {
  const queryClient = useQueryClient()
  return useMutation<ShopOrder, AxiosError<ApiError>, { orderId: number }>({
    mutationFn: ({ orderId }) => $api.shop.cancelMyOrder(orderId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: shopKeys.myOrdersPrefix() })
      queryClient.invalidateQueries({ queryKey: ['points', 'my-balance'] })
      queryClient.invalidateQueries({ queryKey: ['points', 'my-transactions'] })
    },
  })
}

export const useMyDigitalInventory = (
  config?: QueryConfig<ShopPaginated<DigitalInventoryItem>>,
) => {
  return useQuery<ShopPaginated<DigitalInventoryItem>, AxiosError<ApiError>>({
    queryKey: shopKeys.myInventory(),
    queryFn: () => $api.shop.getMyInventory(),
    ...config,
  })
}

export const useEquipDigitalInventoryItem = () => {
  const queryClient = useQueryClient()
  return useMutation<DigitalInventoryItem, AxiosError<ApiError>, { inventoryId: number }>({
    mutationFn: ({ inventoryId }) => $api.shop.equipInventoryItem(inventoryId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: shopKeys.myInventoryPrefix() })
      queryClient.invalidateQueries({ queryKey: ['accounts', 'profile'] })
      queryClient.invalidateQueries({ queryKey: ['accounts', 'users'] })
    },
  })
}

export const useUnequipDigitalInventoryItem = () => {
  const queryClient = useQueryClient()
  return useMutation<DigitalInventoryItem, AxiosError<ApiError>, { inventoryId: number }>({
    mutationFn: ({ inventoryId }) => $api.shop.unequipInventoryItem(inventoryId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: shopKeys.myInventoryPrefix() })
      queryClient.invalidateQueries({ queryKey: ['accounts', 'profile'] })
      queryClient.invalidateQueries({ queryKey: ['accounts', 'users'] })
    },
  })
}

export const useAdminShopCategories = (
  args: { page?: MaybeRefOrGetter<number>; pageSize?: MaybeRefOrGetter<number> } = {},
  config?: QueryConfig<ShopPaginated<ShopCategory>>,
) => {
  return useQuery<ShopPaginated<ShopCategory>, AxiosError<ApiError>>({
    queryKey: computed(() =>
      shopKeys.adminCategories({ page: toValue(args.page) ?? 1, pageSize: toValue(args.pageSize) ?? 100 }),
    ),
    queryFn: () =>
      $api.shop.getAdminCategories({ page: toValue(args.page) ?? 1, pageSize: toValue(args.pageSize) ?? 100 }),
    ...config,
  })
}

export const useAdminShopProducts = (
  args: {
    page?: MaybeRefOrGetter<number>
    pageSize?: MaybeRefOrGetter<number>
    search?: MaybeRefOrGetter<string>
    category?: MaybeRefOrGetter<number | null>
    productType?: MaybeRefOrGetter<'physical' | 'digital' | 'all'>
  } = {},
  config?: QueryConfig<ShopPaginated<ShopProduct>>,
) => {
  return useQuery<ShopPaginated<ShopProduct>, AxiosError<ApiError>>({
    queryKey: computed(() =>
      shopKeys.adminProducts({
        page: toValue(args.page) ?? 1,
        pageSize: toValue(args.pageSize) ?? 20,
        search: toValue(args.search) ?? '',
        category: toValue(args.category) ?? null,
        productType: toValue(args.productType) ?? 'all',
      }),
    ),
    queryFn: () =>
      $api.shop.getAdminProducts({
        page: toValue(args.page) ?? 1,
        pageSize: toValue(args.pageSize) ?? 20,
        search: toValue(args.search) ?? '',
        category: toValue(args.category) ?? null,
        productType: toValue(args.productType) ?? 'all',
      }),
    ...config,
  })
}

export const useAdminShopOrders = (
  args: {
    page?: MaybeRefOrGetter<number>
    pageSize?: MaybeRefOrGetter<number>
    status?: MaybeRefOrGetter<string>
    user?: MaybeRefOrGetter<string>
  } = {},
  config?: QueryConfig<ShopPaginated<ShopOrder>>,
) => {
  return useQuery<ShopPaginated<ShopOrder>, AxiosError<ApiError>>({
    queryKey: computed(() =>
      shopKeys.adminOrders({
        page: toValue(args.page) ?? 1,
        pageSize: toValue(args.pageSize) ?? 20,
        status: toValue(args.status) ?? '',
        user: toValue(args.user) ?? '',
      }),
    ),
    queryFn: () =>
      $api.shop.getAdminOrders({
        page: toValue(args.page) ?? 1,
        pageSize: toValue(args.pageSize) ?? 20,
        status: toValue(args.status) ?? '',
        user: toValue(args.user) ?? '',
      }),
    ...config,
  })
}

export const useAdminCreateCategory = () => {
  const queryClient = useQueryClient()
  return useMutation<ShopCategory, AxiosError<ApiError>, UpsertCategoryBody>({
    mutationFn: (body) => $api.shop.createAdminCategory(body),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: shopKeys.adminCategoriesPrefix() }),
  })
}

export const useAdminUpdateCategory = () => {
  const queryClient = useQueryClient()
  return useMutation<ShopCategory, AxiosError<ApiError>, { id: number; body: Partial<UpsertCategoryBody> }>({
    mutationFn: ({ id, body }) => $api.shop.updateAdminCategory(id, body),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: shopKeys.adminCategoriesPrefix() }),
  })
}

export const useAdminDeleteCategory = () => {
  const queryClient = useQueryClient()
  return useMutation<void, AxiosError<ApiError>, { id: number }>({
    mutationFn: ({ id }) => $api.shop.deleteAdminCategory(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: shopKeys.adminCategoriesPrefix() })
      queryClient.invalidateQueries({ queryKey: shopKeys.adminProductsPrefix() })
      queryClient.invalidateQueries({ queryKey: shopKeys.productsPrefix() })
    },
  })
}

export const useAdminCreateProduct = () => {
  const queryClient = useQueryClient()
  return useMutation<ShopProduct, AxiosError<ApiError>, UpsertProductBody>({
    mutationFn: (body) => $api.shop.createAdminProduct(body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: shopKeys.adminProductsPrefix() })
      queryClient.invalidateQueries({ queryKey: shopKeys.productsPrefix() })
    },
  })
}

export const useAdminUpdateProduct = () => {
  const queryClient = useQueryClient()
  return useMutation<ShopProduct, AxiosError<ApiError>, { id: number; body: Partial<UpsertProductBody> }>({
    mutationFn: ({ id, body }) => $api.shop.updateAdminProduct(id, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: shopKeys.adminProductsPrefix() })
      queryClient.invalidateQueries({ queryKey: shopKeys.productsPrefix() })
    },
  })
}

export const useAdminDeleteProduct = () => {
  const queryClient = useQueryClient()
  return useMutation<void, AxiosError<ApiError>, { id: number }>({
    mutationFn: ({ id }) => $api.shop.deleteAdminProduct(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: shopKeys.adminProductsPrefix() })
      queryClient.invalidateQueries({ queryKey: shopKeys.productsPrefix() })
    },
  })
}

export const useAdminUpdateOrderStatus = () => {
  const queryClient = useQueryClient()
  return useMutation<ShopOrder, AxiosError<ApiError>, { orderId: number; body: UpdateOrderStatusBody }>({
    mutationFn: ({ orderId, body }) => $api.shop.updateAdminOrderStatus(orderId, body),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: shopKeys.adminOrdersPrefix() }),
  })
}

export const useAdminCancelOrder = () => {
  const queryClient = useQueryClient()
  return useMutation<ShopOrder, AxiosError<ApiError>, { orderId: number }>({
    mutationFn: ({ orderId }) => $api.shop.cancelAdminOrder(orderId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: shopKeys.adminOrdersPrefix() }),
  })
}
