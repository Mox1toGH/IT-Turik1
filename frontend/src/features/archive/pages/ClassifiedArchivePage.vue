<template>
  <main
    class="computer"
    :class="{
      booting,
      'crt-glitch': glitching,
      'user-typing': isUserTyping,
      'triangle-blink': triangleBlink,
    }"
  >
    <div class="screen-noise" aria-hidden="true"></div>
    <section class="monitor" aria-label="Secret Archive Computer">
      <Transition name="boot-fade">
        <div v-if="booting" class="boot-screen">
          <div class="boot-head">
            <img :src="triangle" alt="" /><span>NORTHSTAR FIELD SYSTEM</span><b>REV 1987.04</b>
          </div>
          <div class="boot-log" aria-live="polite">
            <p
              v-for="(line, index) in bootLines.slice(0, bootStep)"
              :key="line"
              :class="{ warning: index === 3 }"
            >
              <span>{{ line }}</span
              ><b> [ {{ index === 3 ? 'UNRESOLVED' : 'OK' }} ]</b>
            </p>
            <p v-if="bootStep < bootLines.length" class="boot-current"><i></i> {{ bootStatus }}</p>
          </div>
          <div class="boot-bottom">
            <span>MEMORY CHECK {{ Math.min(bootStep * 25, 100) }}%</span>
            <div><i :style="{ width: `${Math.min(bootStep * 25, 100)}%` }"></i></div>
            <span>PRESS SKIP TO CONTINUE</span>
          </div>
          <button class="skip-boot" type="button" @click="finishBoot">SKIP BOOT в†—</button>
        </div>
      </Transition>

      <div class="computer-ui" :inert="booting" @pointermove="onPointerMove">
        <canvas
          ref="noiseCanvas"
          class="post-boot-noise"
          :style="noiseStyle"
          aria-hidden="true"
        ></canvas>
        <header class="old-computer-bar">
          <div class="machine-name">
            <span class="machine-light"></span><span>FIELD COMPUTER 04</span>
          </div>
          <span class="bar-message">{{ barMessage }}</span>
          <div class="machine-tools">
            <span>{{ clock }}</span
            ><RouterLink to="/team" aria-label="Exit archive">EXIT ↵</RouterLink>
          </div>
        </header>

        <section
          class="single-window archive-window"
          :class="{ 'window-interference': glitching }"
          aria-label="Archive computer"
        >
          <div class="window-title">
            <span
              ><i></i>
              {{
                currentFolder ? `${currentFolder.name} — DIRECTORY` : 'FOUND ARCHIVE — INDEX'
              }}</span
            ><span class="window-controls" aria-hidden="true">− ▣ ×</span>
          </div>
          <div class="archive-shell">
            <Transition name="computer-window" mode="out-in">
              <section v-if="!currentFolder" key="home" class="archive-home">
                <div class="computer-message">
                  <div class="message-copy">
                    <span class="message-label">INCOMING MESSAGE</span>
                    <p aria-live="polite">{{ typedMessage }}<i class="text-cursor"></i></p>
                  </div>
                  <button
                    ref="triangleButton"
                    class="watching-symbol"
                    type="button"
                    aria-label="The archive symbol"
                    @click="triangleReact"
                  >
                    <img :src="triangle" alt="" />
                  </button>
                </div>
                <div class="files-heading">
                  <span>FOUND MATERIAL // PHOTO INDEX</span
                  ><span
                    >{{ visitedFolders.length }} DIRECTORIES REVIEWED<span v-if="photosUnlocked">
                      · INDEX UNSEALED</span
                    ></span
                  >
                </div>
                <div class="folder-grid" aria-label="Archive folders">
                  <button
                    v-for="folder in archiveFolders"
                    :key="folder.id"
                    type="button"
                    class="folder-card"
                    @click="openFolder(folder)"
                  >
                    <span class="folder-icon" aria-hidden="true">▰</span
                    ><span class="folder-info"
                      ><b>{{ folder.name }}/</b><small>{{ folder.description }}</small
                      ><small>{{ folder.files.length }} ITEMS</small></span
                    ><span class="folder-arrow">›</span>
                  </button>
                </div>
                <div class="console" aria-label="Archive terminal">
                  <div class="console-heading">
                    <span><i class="console-led"></i> NS/09 ARCHIVE ACCESS</span
                    ><span>INPUT: OPTIONAL</span>
                  </div>
                  <div ref="terminalOutput" class="console-output" aria-live="polite">
                    <p
                      v-for="(line, index) in terminalLines"
                      :key="`${index}-${line}`"
                      :class="{
                        'console-command': line.startsWith('>'),
                        'console-warning': line.startsWith('!'),
                      }"
                    >
                      {{ line }}
                    </p>
                  </div>
                  <form class="console-input" @submit.prevent="submitCommand">
                    <label for="terminal-command" class="console-prompt"
                      >NS09:ARCHIVE<span class="prompt-mark">›</span
                      ><i class="prompt-cursor" aria-hidden="true"></i></label
                    ><input
                      id="terminal-command"
                      v-model="command"
                      autocomplete="off"
                      spellcheck="false"
                      aria-label="Optional terminal command"
                      placeholder="help / folders / open SWITZERLAND"
                      @input="registerUserTyping"
                    /><button type="submit" aria-label="Send command">↵</button>
                  </form>
                </div>
                <p class="window-footnote">
                  THE INDEX WAS RECOVERED IN A MACHINE THAT WAS STILL RUNNING.
                </p>
              </section>
              <ArchiveFolderContents
                v-else
                :key="`folder-${currentFolder.id}`"
                :folder="currentFolder"
                @back="closeFolder"
                @open-file="selectFile"
              />
            </Transition>

            <Transition name="viewer-fade">
              <ArchivePasswordDialog
                v-if="passwordFile"
                :file="passwordFile"
                :error="passwordError"
                @close="closePassword"
                @submit="submitPassword"
              />
            </Transition>

            <Transition name="viewer-fade">
              <ArchivePhotoViewer
                v-if="activePhoto"
                :photo="activePhoto"
                :photos="viewerFiles"
                :index="photoIndex"
                @close="closeViewer"
                @navigate="onViewerNavigate"
              />
            </Transition>
          </div>
        </section>

        <footer class="computer-taskbar">
          <span><img :src="triangle" alt="" /> FIELD COMPUTER</span
          ><span><i></i> SOMEONE LEFT THE SIGNAL ON</span><span>{{ clock }} <b>·</b> DISK 01</span>
        </footer>
      </div>
      <div class="bezel-label">
        <span>NS—09</span><span>MAGNETIC FIELD DISPLAY / MODEL 04</span><span>◉</span>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { archiveFolders, type ArchiveFolder, type ArchivePhotoFile } from '../data/foundArchive'
import ArchiveFolderContents from '../components/ArchiveFolderContents.vue'
import ArchivePasswordDialog from '../components/ArchivePasswordDialog.vue'
import ArchivePhotoViewer from '../components/ArchivePhotoViewer.vue'
import { useArchiveBoot } from '../composables/useArchiveBoot'
import { useArchiveProgress } from '../composables/useArchiveProgress'
import { useArchiveTerminal } from '../composables/useArchiveTerminal'
import { useStaticNoise } from '../../../composables/useStaticNoise'
import triangle from '@/assets/triangle.jpg'
import { AXIOS_INSTANCE } from '../../../lib/apiClient'

const { bootLines, bootStatus, booting, bootStep, finishBoot } = useArchiveBoot()
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
const { visitedFolders, photosUnlocked, markFolderVisited } = useArchiveProgress()
const {
  canvasRef: noiseCanvas,
  canvasStyle: noiseStyle,
  start: startNoise,
} = useStaticNoise({ opacity: 0.19, mobileQuery: '(max-width: 760px)' })
const triangleButton = ref<HTMLButtonElement | null>(null)
const triangleBlink = ref(false)
const barMessage = ref('LEFT RUNNING. NO ONE CLAIMS IT.')
const glitching = ref(false)
const currentFolder = ref<ArchiveFolder | null>(null)
const activePhoto = ref<ArchivePhotoFile | null>(null)
const viewerFiles = ref<ArchivePhotoFile[]>([])
const photoIndex = ref(0)
const passwordFile = ref<ArchivePhotoFile | null>(null)
const passwordError = ref('')
const repairedFileIds = ref<string[]>([])
const isRepairing = ref(false)
const clock = ref(
  new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false }),
)
let clockTimer: ReturnType<typeof setInterval> | undefined
let glitchTimer: ReturnType<typeof setTimeout> | undefined
let triangleTimer: ReturnType<typeof setTimeout> | undefined
let repairTimer: ReturnType<typeof setTimeout> | undefined
const folderFiles = computed(() => currentFolder.value?.files ?? [])

function triggerGlitch(duration = 350) {
  glitching.value = true
  if (glitchTimer) clearTimeout(glitchTimer)
  glitchTimer = setTimeout(() => (glitching.value = false), duration)
}
function openFolder(folder: ArchiveFolder) {
  currentFolder.value = folder
  markFolderVisited(folder.id)
  triggerGlitch(160)
}
function closeFolder() {
  closeViewer()
  currentFolder.value = null
  triggerGlitch(180)
}
function selectFile(file: ArchivePhotoFile) {
  if (file.corrupted && !repairedFileIds.value.includes(file.id)) {
    passwordFile.value = file
    passwordError.value = ''
    return
  }
  openPhoto(file)
}
async function submitPassword(password: string) {
  let valid = false
  try {
    const response = await AXIOS_INSTANCE.post<{ valid: boolean }>(
      '/api/archive/verify-corrupted-password',
      { password },
    )
    valid = response.data.valid
  } catch {
    passwordError.value = '! AUTHENTICATION SERVICE UNAVAILABLE'
    return
  }
  if (!valid) {
    passwordError.value = '! AUTHENTICATION FAILED // KEY NOT RECOGNIZED'
    appendLines([`! RECOVERY REJECTED FOR ${passwordFile.value?.filename ?? 'UNKNOWN FILE'}.`])
    triggerGlitch(260)
    return
  }
  const file = passwordFile.value
  if (!file) return
  repairedFileIds.value.push(file.id)
  file.thumb = file.src
  passwordFile.value = null
  isRepairing.value = true
  repairTimer = setTimeout(
    () => {
      isRepairing.value = false
      openPhoto(file)
    },
    reducedMotion ? 120 : 700,
  )
}
function closePassword() {
  passwordFile.value = null
  passwordError.value = ''
}
function openPhoto(file: ArchivePhotoFile) {
  viewerFiles.value = folderFiles.value
  photoIndex.value = Math.max(
    0,
    viewerFiles.value.findIndex((entry) => entry.id === file.id),
  )
  activePhoto.value = file
}
function onViewerNavigate(file: ArchivePhotoFile, index: number) {
  activePhoto.value = file
  photoIndex.value = index
}
function closeViewer() {
  activePhoto.value = null
}
function onKeydown(event: KeyboardEvent) {
  if (passwordFile.value && event.key === 'Escape') closePassword()
}
function updateClock() {
  clock.value = new Date().toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })
}
function onPointerMove(event: PointerEvent) {
  const symbol = triangleButton.value
  if (!symbol || event.pointerType === 'touch') return
  const rect = symbol.getBoundingClientRect()
  const dx = event.clientX - (rect.left + rect.width / 2)
  const dy = event.clientY - (rect.top + rect.height / 2)
  const distance = Math.hypot(dx, dy)
  const amount = distance < 240 ? (1 - distance / 240) * 5 : 0
  symbol.style.setProperty('--gaze-x', `${distance ? (dx / distance) * amount : 0}px`)
  symbol.style.setProperty('--gaze-y', `${distance ? (dy / distance) * amount : 0}px`)
}
function triangleReact() {
  triangleBlink.value = true
  triggerGlitch(420)
  if (triangleTimer) clearTimeout(triangleTimer)
  triangleTimer = setTimeout(() => (triangleBlink.value = false), 700)
}
const {
  command,
  terminalLines,
  terminalOutput,
  typedMessage,
  isUserTyping,
  appendLines,
  submitCommand,
  registerUserTyping,
  start: startTerminal,
} = useArchiveTerminal({
  reducedMotion,
  openFolder: (name) => {
    const folder = archiveFolders.find((entry) => entry.name === name)
    if (!folder) return false
    openFolder(folder)
    return true
  },
})
watch(booting, (loading, wasLoading) => {
  if (wasLoading && !loading) {
    startTerminal()
    startNoise()
  }
})
onMounted(() => {
  clockTimer = setInterval(updateClock, 15000)
  window.addEventListener('keydown', onKeydown)
})
onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
  ;[clockTimer, glitchTimer, triangleTimer, repairTimer].forEach(
    (timer) => timer && clearTimeout(timer),
  )
})
</script>

<style scoped src="./ClassifiedArchivePage.css"></style>
