import { onMounted, onUnmounted, ref } from 'vue'

export function useConnection() {
  const isOnline = ref(typeof navigator !== 'undefined' ? navigator.onLine : true)

  const update = () => {
    isOnline.value = navigator.onLine
  }

  onMounted(() => {
    window.addEventListener('online', update)
    window.addEventListener('offline', update)
  })

  onUnmounted(() => {
    window.removeEventListener('online', update)
    window.removeEventListener('offline', update)
  })

  return { isOnline }
}
