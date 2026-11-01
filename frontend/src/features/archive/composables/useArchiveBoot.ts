import { onMounted, onUnmounted, ref } from 'vue'

const bootMessages = [
  'INITIALIZING DEVICE...',
  'VERIFYING LOCAL CACHE...',
  'INDEXING PERSONNEL FILES...',
  'SIGNAL SOURCE UNRESOLVED...',
  'DESKTOP READY.',
]

export function useArchiveBoot() {
  const bootLines = [
    'NS/09 MEMORY CHECK',
    'ENCRYPTED CHANNEL',
    'PERSONNEL INDEX',
    'UNKNOWN PROCESS // SESSION 0x1',
    'ARCHIVE MOUNT',
  ]
  const bootStatus = ref('INITIALIZING DEVICE...')
  const booting = ref(true)
  const bootStep = ref(0)

  let bootTimer: ReturnType<typeof setInterval> | undefined

  function finishBoot() {
    booting.value = false
    if (bootTimer) clearInterval(bootTimer)
  }

  onMounted(() => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) finishBoot()
    else {
      bootTimer = setInterval(() => {
        bootStep.value += 1
        bootStatus.value = bootMessages[Math.min(bootStep.value, bootMessages.length - 1)]!
        if (bootStep.value >= bootLines.length) finishBoot()
      }, 430)
    }
  })

  onUnmounted(() => {
    if (bootTimer) clearInterval(bootTimer)
  })

  return { bootLines, bootStatus, booting, bootStep, finishBoot }
}
