import { ref } from 'vue'
import { useGetMyPointsBalance } from '@/api/points/points'
import { usePurchaseProduct } from '@/api/shop/shop'
import { useNotification } from '@/composables/useNotification'
import type { Product } from '@/api/.ts.schemas'

/** Баланс користувача + купівля товару. */
export function useProductPurchase() {
  const { showNotification } = useNotification()
  const { data: pointsBalance } = useGetMyPointsBalance()
  const { mutate: purchase, isPending: isPurchasePending } = usePurchaseProduct()

  const isDetailOpen = ref(false)
  const activeProduct = ref<Product | null>(null)

  const openProductDetail = (product: Product) => {
    activeProduct.value = product
    isDetailOpen.value = true
  }

  const handlePurchase = (payload: { productId: number; quantity: number }) => {
    purchase(
      { data: { product_id: payload.productId, quantity: payload.quantity } },
      {
        onSuccess: (res) => {
          showNotification(`Purchase successful. Order #${res.id} (${res.status}).`, 'success')
          isDetailOpen.value = false
        },
        onError: (error) => showNotification(error?.message ?? 'Purchase failed.', 'error'),
      },
    )
  }

  return {
    pointsBalance,
    isPurchasePending,
    isDetailOpen,
    activeProduct,
    openProductDetail,
    handlePurchase,
  }
}
