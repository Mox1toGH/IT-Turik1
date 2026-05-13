import { apiClient } from '@/api/client'
import type {
  GetProductsArgs,
  PurchaseBody,
  DigitalInventoryItem,
  ShopCategory,
  ShopOrder,
  ShopPaginated,
  ShopProduct,
  UpdateOrderStatusBody,
  UpsertCategoryBody,
  UpsertProductBody,
} from './types'

const prefix = '/api/shop'

export const shopService = {
  buildProductPayload(body: UpsertProductBody | Partial<UpsertProductBody>) {
    const hasImages = Array.isArray(body.uploaded_images) && body.uploaded_images.length > 0
    if (!hasImages) return body

    const formData = new FormData()
    if (body.name !== undefined) formData.append('name', String(body.name))
    if (body.description !== undefined) formData.append('description', String(body.description))
    if (body.price !== undefined) formData.append('price', String(body.price))
    if (body.stock_quantity !== undefined)
      formData.append('stock_quantity', String(body.stock_quantity))
    if (body.category_id !== undefined) formData.append('category_id', String(body.category_id))
    if (body.product_type !== undefined) formData.append('product_type', String(body.product_type))
    if (body.digital_asset_url !== undefined) formData.append('digital_asset_url', String(body.digital_asset_url))
    if (body.is_active !== undefined) formData.append('is_active', String(body.is_active))
    for (const image of body.uploaded_images || []) {
      formData.append('uploaded_images', image)
    }
    return formData
  },

  async getProducts(args: GetProductsArgs = {}) {
    const { data } = await apiClient.get<ShopPaginated<ShopProduct>>(`${prefix}/products/`, {
      params: {
        page: args.page ?? 1,
        page_size: args.pageSize ?? 20,
        search: args.search || undefined,
        category: args.category || undefined,
        product_type: args.productType && args.productType !== 'all' ? args.productType : undefined,
        ordering: args.ordering ?? 'name',
      },
    })
    return data
  },

  async getProduct(id: number) {
    const { data } = await apiClient.get<ShopProduct>(`${prefix}/products/${id}/`)
    return data
  },

  async purchase(body: PurchaseBody) {
    const { data } = await apiClient.post<ShopOrder>(`${prefix}/purchase/`, body)
    return data
  },

  async getMyOrders(args: { page?: number; pageSize?: number } = {}) {
    const { data } = await apiClient.get<ShopPaginated<ShopOrder>>(`${prefix}/orders/my/`, {
      params: { page: args.page ?? 1, page_size: args.pageSize ?? 20 },
    })
    return data
  },

  async cancelMyOrder(orderId: number) {
    const { data } = await apiClient.post<ShopOrder>(`${prefix}/orders/my/${orderId}/cancel/`)
    return data
  },

  async getMyInventory() {
    const { data } = await apiClient.get<ShopPaginated<DigitalInventoryItem>>(`${prefix}/inventory/my/`, {
      params: { page_size: 100 },
    })
    return data
  },

  async equipInventoryItem(inventoryId: number) {
    const { data } = await apiClient.post<DigitalInventoryItem>(`${prefix}/inventory/equip/`, {
      inventory_id: inventoryId,
    })
    return data
  },

  async unequipInventoryItem(inventoryId: number) {
    const { data } = await apiClient.post<DigitalInventoryItem>(`${prefix}/inventory/unequip/`, {
      inventory_id: inventoryId,
    })
    return data
  },

  async getAdminCategories(args: { page?: number; pageSize?: number } = {}) {
    const { data } = await apiClient.get<ShopPaginated<ShopCategory>>(
      `${prefix}/admin/categories/`,
      {
        params: { page: args.page ?? 1, page_size: args.pageSize ?? 100 },
      },
    )
    return data
  },

  async createAdminCategory(body: UpsertCategoryBody) {
    const { data } = await apiClient.post<ShopCategory>(`${prefix}/admin/categories/`, body)
    return data
  },

  async updateAdminCategory(id: number, body: Partial<UpsertCategoryBody>) {
    const { data } = await apiClient.patch<ShopCategory>(`${prefix}/admin/categories/${id}/`, body)
    return data
  },

  async deleteAdminCategory(id: number) {
    await apiClient.delete(`${prefix}/admin/categories/${id}/`)
  },

  async getAdminProducts(args: GetProductsArgs = {}) {
    const { data } = await apiClient.get<ShopPaginated<ShopProduct>>(`${prefix}/admin/products/`, {
      params: {
        page: args.page ?? 1,
        page_size: args.pageSize ?? 20,
        search: args.search || undefined,
        category: args.category || undefined,
        product_type: args.productType && args.productType !== 'all' ? args.productType : undefined,
      },
    })
    return data
  },

  async createAdminProduct(body: UpsertProductBody) {
    const payload = this.buildProductPayload(body)
    const { data } = await apiClient.post<ShopProduct>(`${prefix}/admin/products/`, payload)
    return data
  },

  async updateAdminProduct(id: number, body: Partial<UpsertProductBody>) {
    const payload = this.buildProductPayload(body)
    const { data } = await apiClient.patch<ShopProduct>(`${prefix}/admin/products/${id}/`, payload)
    return data
  },

  async deleteAdminProduct(id: number) {
    await apiClient.delete(`${prefix}/admin/products/${id}/`)
  },

  async getAdminOrders(
    args: { page?: number; pageSize?: number; status?: string; user?: string } = {},
  ) {
    const { data } = await apiClient.get<ShopPaginated<ShopOrder>>(`${prefix}/admin/orders/`, {
      params: {
        page: args.page ?? 1,
        page_size: args.pageSize ?? 20,
        status: args.status || undefined,
        user: args.user || undefined,
      },
    })
    return data
  },

  async updateAdminOrderStatus(orderId: number, body: UpdateOrderStatusBody) {
    const { data } = await apiClient.patch<ShopOrder>(
      `${prefix}/admin/orders/${orderId}/status/`,
      body,
    )
    return data
  },

  async cancelAdminOrder(orderId: number) {
    const { data } = await apiClient.post<ShopOrder>(`${prefix}/admin/orders/${orderId}/cancel/`)
    return data
  },
}
