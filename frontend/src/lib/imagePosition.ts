export type ImagePosition = {
  x: number
  y: number
}

const DEFAULT_POSITION: ImagePosition = { x: 50, y: 50 }

const clamp = (value: number) => Math.min(100, Math.max(0, value))

export const toObjectPosition = (position: ImagePosition) =>
  `${clamp(position.x)}% ${clamp(position.y)}%`

export const readImagePosition = (key?: string): ImagePosition => {
  if (!key) return DEFAULT_POSITION
  try {
    const raw = localStorage.getItem(key)
    if (!raw) return DEFAULT_POSITION
    const parsed = JSON.parse(raw) as Partial<ImagePosition>
    if (typeof parsed.x !== 'number' || typeof parsed.y !== 'number') return DEFAULT_POSITION
    return { x: clamp(parsed.x), y: clamp(parsed.y) }
  } catch {
    return DEFAULT_POSITION
  }
}

export const writeImagePosition = (key: string, position: ImagePosition) => {
  localStorage.setItem(
    key,
    JSON.stringify({
      x: clamp(position.x),
      y: clamp(position.y),
    }),
  )
}

export const clearImagePosition = (key?: string) => {
  if (!key) return
  localStorage.removeItem(key)
}
