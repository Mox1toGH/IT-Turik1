import { computed, ref, type Ref } from 'vue'
import {
  clearImagePosition,
  readImagePosition,
  toObjectPosition,
  writeImagePosition,
} from '@/lib/imagePosition'

type Position = { x: number; y: number }

const store = new Map<string, Ref<Position>>()

function getPosition(key: string): Ref<Position> {
  let r = store.get(key)
  if (!r) {
    r = ref(readImagePosition(key))
    store.set(key, r)
  }
  return r
}

export function useBannerPosition(tournamentId: number) {
  const key = `image-position:banner:tournament:${tournamentId}`
  const position = getPosition(key)
  const objectPosition = computed(() => toObjectPosition(position.value))

  const save = (next: Position) => {
    position.value = { ...next }
    writeImagePosition(key, next)
  }

  const clear = () => {
    clearImagePosition(key)
    position.value = readImagePosition(key)
  }

  return { position, objectPosition, save, clear }
}
