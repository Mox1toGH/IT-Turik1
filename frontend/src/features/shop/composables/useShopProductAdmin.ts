import { computed, ref } from 'vue'
import {
  useCreateAdminProduct,
  useDeleteAdminProduct,
  useListAvatarFrames,
  useUpdateAdminProduct,
  type CreateAdminProductMutationBody,
} from '@/api/shop/shop'
import { useNotification } from '@/composables/useNotification'
import type { ProductResponse } from '@/api/backendAPINinja.schemas'

export function useShopProductAdmin() {
  const { showNotification } = useNotification()

  const { data: avatarFramesData } = useListAvatarFrames()
  const avatarFrames = computed(() => avatarFramesData.value?.items ?? [])

  const isProductFormOpen = ref(false)
  const editingProduct = ref<ProductResponse | null>(null)
  const isProductDeleteOpen = ref(false)
  const deletingProduct = ref<ProductResponse | null>(null)

  const { mutate: createProduct, isPending: isCreatingProduct } = useCreateAdminProduct()
  const { mutate: updateProduct, isPending: isUpdatingProduct } = useUpdateAdminProduct()
  const { mutate: deleteProduct, isPending: isDeletingProduct } = useDeleteAdminProduct()
  const isSavingProduct = computed(() => isCreatingProduct.value || isUpdatingProduct.value)

  const onError = (error: { message?: string }) => showNotification(error?.message, 'error')

  const openProductCreate = () => {
    editingProduct.value = null
    isProductFormOpen.value = true
  }

  const openProductEdit = (product: ProductResponse) => {
    editingProduct.value = product
    isProductFormOpen.value = true
  }

  const openProductDelete = (product: ProductResponse) => {
    deletingProduct.value = product
    isProductDeleteOpen.value = true
  }

  const submitProductForm = (body: CreateAdminProductMutationBody) => {
    if (!editingProduct.value) {
      createProduct(
        { data: body },
        {
          onSuccess: () => {
            isProductFormOpen.value = false
            showNotification('Product created.', 'success')
          },
          onError,
        },
      )
      return
    }

    updateProduct(
      { productId: editingProduct.value.id, data: body },
      {
        onSuccess: () => {
          isProductFormOpen.value = false
          showNotification('Product updated.', 'success')
        },
        onError,
      },
    )
  }

  const confirmProductDelete = () => {
    if (!deletingProduct.value) return
    deleteProduct(
      { productId: deletingProduct.value.id },
      {
        onSuccess: () => {
          isProductDeleteOpen.value = false
          deletingProduct.value = null
          showNotification('Product deleted.', 'success')
        },
        onError,
      },
    )
  }

  return {
    avatarFrames,
    isProductFormOpen,
    editingProduct,
    isProductDeleteOpen,
    isSavingProduct,
    isDeletingProduct,
    openProductCreate,
    openProductEdit,
    openProductDelete,
    submitProductForm,
    confirmProductDelete,
  }
}
