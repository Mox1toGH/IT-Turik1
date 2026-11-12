import { onMounted, onUnmounted, ref } from 'vue'

const titleSource = 'PEOPLE BEHIND THE PROJECT'
const kickerSource = 'FIELD OFFICE // PERSONNEL INDEX'
const countSource = '04 IDENTITIES VERIFIED · 01 RECORD SEALED'
const glitchSymbols = ['%', '#', '$', '?', '.', '>', '<', '/', '\\', '0', '_', '!']

function corruptText(source: string, minChanges: number, changeRange: number) {
  const corrupted = Array.from(source)
  const positions = corrupted.flatMap((character, index) =>
    character === ' ' || character === '·' ? [] : [index],
  )
  const count = Math.min(positions.length, minChanges + Math.floor(Math.random() * changeRange))
  const changed = new Set<number>()

  while (changed.size < count) changed.add(positions[Math.floor(Math.random() * positions.length)]!)
  for (const position of changed) {
    corrupted[position] = glitchSymbols[Math.floor(Math.random() * glitchSymbols.length)]!
  }

  return corrupted.join('')
}

export function useBoardPreparation() {
  const preparing = ref(true)
  const introTitle = ref(titleSource)
  const introKicker = ref(kickerSource)
  const introCount = ref(countSource)
  const titleGlitch = ref(false)

  let preparationTimer: ReturnType<typeof setTimeout> | undefined
  let titleAnomalyTimer: ReturnType<typeof setTimeout> | undefined
  let titleRestoreTimer: ReturnType<typeof setTimeout> | undefined

  function finishPreparation() {
    preparing.value = false

    if (preparationTimer) clearTimeout(preparationTimer)
    if (titleAnomalyTimer) clearTimeout(titleAnomalyTimer)
    if (titleRestoreTimer) clearTimeout(titleRestoreTimer)

    introTitle.value = titleSource
    introKicker.value = kickerSource
    introCount.value = countSource
    titleGlitch.value = false
  }

  function scheduleTitleAnomaly() {
    titleAnomalyTimer = setTimeout(
      () => {
        if (!preparing.value) return

        titleGlitch.value = true
        introTitle.value = corruptText(titleSource, 5, 5)
        introKicker.value = corruptText(kickerSource, 3, 3)
        introCount.value = corruptText(countSource, 4, 4)

        titleRestoreTimer = setTimeout(
          () => {
            introTitle.value = titleSource
            introKicker.value = kickerSource
            introCount.value = countSource
            titleGlitch.value = false
            scheduleTitleAnomaly()
          },
          150 + Math.random() * 180,
        )
      },
      100 + Math.random() * 200,
    )
  }

  onMounted(() => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) finishPreparation()
    else {
      scheduleTitleAnomaly()
      preparationTimer = setTimeout(finishPreparation, 2600)
    }
  })

  onUnmounted(() => {
    if (preparationTimer) clearTimeout(preparationTimer)
    if (titleAnomalyTimer) clearTimeout(titleAnomalyTimer)
    if (titleRestoreTimer) clearTimeout(titleRestoreTimer)
  })

  return { preparing, introTitle, introKicker, introCount, titleGlitch }
}
