import { computed, ref, watch } from 'vue'
import { useListProducts } from '@/api/shop/shop'

export type ProductType = 'physical' | 'digital' | 'all'
export type ProductOrdering = 'name' | '-name' | 'price' | '-price'

export const typeOptions = [
  { value: 'all', label: 'All types' },
  { value: 'physical', label: 'Physical' },
  { value: 'digital', label: 'Digital' },
]

export const orderingOptions = [
  { value: 'name', label: 'Name A-Z' },
  { value: '-name', label: 'Name Z-A' },
  { value: 'price', label: 'Price low-high' },
  { value: '-price', label: 'Price high-low' },
]

export function useShopCatalog(initialPageSize = 12) {
  const currentPage = ref(1)
  const pageSize = ref(initialPageSize)
  const search = ref('')
  const selectedCategory = ref('all')
  const selectedType = ref<ProductType>('all')
  const selectedOrdering = ref<ProductOrdering>('name')

  const { data, isLoading, isLoadingError, error } = useListProducts(
    computed(() => ({
      page: currentPage.value,
      page_size: pageSize.value,
      search: search.value,
      category: selectedCategory.value === 'all' ? undefined : Number(selectedCategory.value),
      product_type: selectedType.value === 'all' ? undefined : selectedType.value,
      ordering: selectedOrdering.value,
    })),
  )

  const products = computed(() => data.value?.results ?? [])
  const totalCount = computed(() => data.value?.count ?? 0)
  const totalPages = computed(() => Math.max(1, Math.ceil(totalCount.value / pageSize.value)))

  watch([search, selectedCategory, selectedType, selectedOrdering], () => {
    currentPage.value = 1
  })

  const categoryOptions = computed(() => {
    const set = new Map<number, string>()
    for (const item of products.value) set.set(item.category.id, item.category.name)
    return [
      { value: 'all', label: 'All categories' },
      ...Array.from(set.entries()).map(([id, name]) => ({ value: String(id), label: name })),
    ]
  })

  return {
    currentPage,
    pageSize,
    search,
    selectedCategory,
    selectedType,
    selectedOrdering,
    products,
    totalCount,
    totalPages,
    categoryOptions,
    isLoading,
    isLoadingError,
    error,
  }
}
