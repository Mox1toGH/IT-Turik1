import { computed, ref, type Ref } from 'vue'
import {
  useCreateAdminCategory,
  useDeleteAdminCategory,
  useListAdminCategories,
  useUpdateAdminCategory,
} from '@/api/shop/shop'
import { useNotification } from '@/composables/useNotification'

/** Список та CRUD категорій (адмін). */
export function useShopCategoryAdmin(enabled: Ref<boolean>) {
  const { showNotification } = useNotification()

  const { data: adminCategoryData } = useListAdminCategories(void 0, { query: { enabled } })
  const adminCategories = computed(() => adminCategoryData.value?.results ?? [])

  const isCategoryModalOpen = ref(false)
  const openCategoryModal = () => {
    isCategoryModalOpen.value = true
  }

  const { mutate: createCategoryMutation } = useCreateAdminCategory()
  const { mutate: updateCategoryMutation } = useUpdateAdminCategory()
  const { mutate: removeCategoryMutation } = useDeleteAdminCategory()

  const onError = (error: { message?: string }) => showNotification(error?.message, 'error')

  const createCategory = (name: string) =>
    createCategoryMutation(
      { data: { name } },
      { onSuccess: () => showNotification('Category created.', 'success'), onError },
    )

  const updateCategory = (payload: { id: number; name: string }) =>
    updateCategoryMutation(
      { id: payload.id, data: { name: payload.name } },
      { onSuccess: () => showNotification('Category updated.', 'success'), onError },
    )

  const deleteCategory = (id: number) =>
    removeCategoryMutation(
      { id },
      { onSuccess: () => showNotification('Category deleted.', 'success'), onError },
    )

  return {
    adminCategories,
    isCategoryModalOpen,
    openCategoryModal,
    createCategory,
    updateCategory,
    deleteCategory,
  }
}
