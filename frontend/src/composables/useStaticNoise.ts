import { onUnmounted, ref, type CSSProperties } from 'vue'

type NoiseTint = { red: number; green: number; blue: number }

export type StaticNoiseOptions = {
  opacity?: number
  desktopResolution?: { width: number; height: number }
  mobileResolution?: { width: number; height: number }
  mobileQuery?: string
  refreshMs?: number
  grainMin?: number
  grainRange?: number
  alphaMax?: number
  highlightChance?: number
  baseTint?: NoiseTint
  highlightTint?: NoiseTint
}

const computerDefaults: Required<StaticNoiseOptions> = {
  opacity: 0.19,
  desktopResolution: { width: 340, height: 192 },
  mobileResolution: { width: 190, height: 108 },
  mobileQuery: '(max-width: 760px)',
  refreshMs: 100,
  grainMin: 25,
  grainRange: 210,
  alphaMax: 58,
  highlightChance: 0.015,
  baseTint: { red: 0.7, green: 1, blue: 0.72 },
  highlightTint: { red: 1.4, green: 0.8, blue: 1.5 },
}

/** Shared canvas TV static used by the archive computer and investigation board. */
export function useStaticNoise(options: StaticNoiseOptions = {}) {
  const settings: Required<StaticNoiseOptions> = { ...computerDefaults, ...options }
  const canvasRef = ref<HTMLCanvasElement | null>(null)
  const canvasStyle = { '--static-noise-opacity': String(settings.opacity) } as CSSProperties
  let timer: ReturnType<typeof setInterval> | undefined

  function stop() {
    if (timer) clearInterval(timer)
    timer = undefined
  }

  function start() {
    stop()
    const canvas = canvasRef.value
    const context = canvas?.getContext('2d', { alpha: true })
    if (!canvas || !context) return

    const resolution = window.matchMedia(settings.mobileQuery).matches
      ? settings.mobileResolution
      : settings.desktopResolution
    canvas.width = resolution.width
    canvas.height = resolution.height
    const frame = context.createImageData(canvas.width, canvas.height)

    const drawNoise = () => {
      for (let pixel = 0; pixel < frame.data.length; pixel += 4) {
        const grain = Math.random() * settings.grainRange + settings.grainMin
        const highlight = Math.random() < settings.highlightChance
        const tint = highlight ? settings.highlightTint : settings.baseTint
        frame.data[pixel] = Math.min(255, grain * tint.red)
        frame.data[pixel + 1] = Math.min(255, grain * tint.green)
        frame.data[pixel + 2] = Math.min(255, grain * tint.blue)
        frame.data[pixel + 3] = Math.random() * settings.alphaMax
      }
      context.putImageData(frame, 0, 0)
    }

    drawNoise()
    if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      timer = setInterval(drawNoise, settings.refreshMs)
    }
  }

  onUnmounted(stop)
  return { canvasRef, canvasStyle, start, stop }
}
