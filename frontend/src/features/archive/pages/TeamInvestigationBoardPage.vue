<template>
  <main
    class="investigation-page"
    :class="[
      `tap-stage-${sealStage}`,
      sealResetting ? `reset-from-${resetVisualStage}` : '',
      {
        'board-ready': !preparing,
        'is-preparing': preparing,
        'seal-flash': sealStage === 5,
        'seal-fading': sealFading,
        'seal-resetting': sealResetting,
      },
    ]"
    :style="sealSymbolStyle"
  >
    <Transition name="preparation-backdrop">
      <div v-if="preparing" class="preparation-backdrop" aria-hidden="true"></div>
    </Transition>
    <canvas
      ref="boardNoise"
      class="board-static"
      :style="boardNoiseStyle"
      aria-hidden="true"
    ></canvas>
    <Transition name="preparation">
      <section
        v-if="preparing"
        class="preparation-screen"
        :class="{ 'signal-glitch': titleGlitch }"
        aria-hidden="true"
      >
        <div class="intro-title-wrap">
          <span class="intro-kicker">{{ introKicker }}</span>
          <h2 class="intro-title" :class="{ 'title-glitch': titleGlitch }" :data-text="introTitle">
            {{ introTitle }}
          </h2>
          <span class="intro-count">{{ introCount }}</span>
        </div>
      </section>
    </Transition>
    <header class="board-heading" :class="`stage-${sealStage}`" :inert="preparing">
      <div
        class="heading-seal"
        :class="`stage-${sealStage}`"
        @pointerdown.stop.prevent="advanceSeal"
      >
        <img :src="triangle" alt="" draggable="false" /><span
          v-if="sealStage >= 2"
          class="seal-signal"
          aria-hidden="true"
          >{{ sealSignalLabel }}</span
        >
      </div>
      <h1>THE PEOPLE BEHIND <em>THE PROJECT</em></h1>
    </header>
    <section
      class="board-frame"
      :inert="preparing"
      aria-label="Mystery investigation board with five personnel records"
    >
      <div class="board-surface">
        <BoardJournalLayer />
        <svg
          class="red-strings"
          viewBox="0 0 1200 690"
          preserveAspectRatio="none"
          aria-hidden="true"
        >
          <path
            class="string-shadow"
            d="M200 150 C280 245 438 230 600 144 S907 99 1000 150 C980 278 817 357 800 495 S566 521 400 500 C359 361 225 276 200 150Z"
          />
          <path
            class="string-main"
            d="M200 150 C280 245 438 230 600 144 S907 99 1000 150 C980 278 817 357 800 495 S566 521 400 500 C359 361 225 276 200 150Z"
          />
          <path
            class="string-main loose"
            d="M200 150 Q600 330 1000 150 M200 150 Q323 413 400 500 M600 144 Q705 350 800 495 M1000 150 Q895 337 800 495 M400 500 Q590 420 800 495"
          />
          <circle cx="600" cy="144" r="5" />
          <circle cx="1000" cy="150" r="5" />
          <circle cx="800" cy="495" r="5" />
          <circle cx="400" cy="500" r="5" />
        </svg>

        <div class="board-sticker sticker-left">EVERY TRAIL<br />LEADS BACK HERE</div>
        <div class="board-sticker sticker-right">WHO PUT THIS<br />ON THE WALL?</div>
        <div v-for="note in pinnedNotes" :key="note.id" class="pinned-note" :class="note.placement">
          {{ note.text }}<span>{{ note.detail }}</span>
        </div>
        <button
          class="evidence-slip"
          type="button"
          :aria-expanded="evidenceRevealed"
          aria-label="Inspect the recovered field tape"
          @click="evidenceRevealed = !evidenceRevealed"
        >
          <span>{{ evidenceRevealed ? 'FIELD TAPE / SIDE B' : 'FIELD TAPE / SIDE A' }}</span>
          <b>{{ evidenceRevealed ? 'SIX VOICES' : '5 PEOPLE' }}</b>
          <i>{{ evidenceRevealed ? 'SOURCE: UNCONNECTED' : '1 SHARED PROJECT' }}</i>
          <small>{{
            evidenceRevealed ? 'RECORDING ENDS BEFORE IT BEGINS' : 'COINCIDENCE? · INSPECT'
          }}</small>
          <span class="tape-reels" aria-hidden="true"><i></i><i></i></span>
        </button>

        <div class="board-grid">
          <article
            v-for="(member, index) in members"
            :key="member.id"
            class="person-note"
            :class="`person-note-${index + 1}`"
            @click="openMember(index)"
          >
            <span class="pushpin" :class="`pin-${index + 1}`" aria-hidden="true"></span>
            <button
              class="photo-file"
              type="button"
              :aria-label="`Open file ${index + 1}: ${member.name}`"
            >
              <span class="photo-area" :class="{ 'has-member-photo': member.photo }">
                <img
                  v-if="member.photo"
                  class="member-photo-image"
                  :src="member.photo"
                  :alt="member.name"
                />
                <img v-else class="photo-sigil" :src="triangle" alt="" />
                <span v-if="!member.photo" class="photo-placeholder"
                  ><b>{{ member.photoMark }}</b
                  ><small>PHOTO<br />NOT ON FILE</small></span
                >
                <span class="photo-number">00{{ index + 1 }}</span>
              </span>
              <span class="photo-caption"
                >PERSON_00{{ index + 1 }} <small>· {{ member.kind }}</small></span
              >
            </button>
            <div class="identity-strip">
              <h2>{{ member.name }}</h2>
              <p>{{ member.role }}</p>
              <span class="work-focus">{{ member.focus }}</span>
            </div>
            <div class="contact-row" :aria-label="`Links for ${member.name}`">
              <span v-if="!member.links.length" class="contact-placeholder" title="No links added"
                >—</span
              >
              <a
                v-for="link in member.links"
                :key="link.href"
                class="member-link"
                :href="link.href"
                :aria-label="link.icon.title"
                :title="link.icon.title"
                target="_blank"
                rel="noopener noreferrer"
                @click.stop
              >
                <svg viewBox="0 0 24 24" aria-hidden="true"><path :d="link.icon.path" /></svg>
              </a>
              <button
                type="button"
                class="file-open"
                :aria-label="`Read the case note for ${member.name}`"
              >
                READ FILE ↗
              </button>
            </div>
          </article>
        </div>

        <div class="map-scrap" aria-hidden="true">
          <span class="map-title">LOCAL AREA / NOT TO SCALE</span>
          <svg viewBox="0 0 170 100">
            <path
              d="M6 78 24 63 30 35 57 41 74 18 97 25 109 54 139 48 160 71 143 88 115 79 90 91 60 76 36 91Z"
            />
            <path d="m28 64 29-23 20-23m20 7-5 29 47-6m-30 25-19 18-30-15" />
            <circle cx="99" cy="54" r="4" />
            <path d="m99 45 0-18m0 36v17m-8-26H73m51 0h18" />
          </svg>
          <small>MARKED IN RED<br />FOR NO REASON</small>
        </div>
        <button
          class="tape-note"
          type="button"
          :aria-expanded="noteRevealed"
          aria-label="Inspect the note found under the radio"
          @click="noteRevealed = !noteRevealed"
        >
          <span v-if="!noteRevealed">{{ tapeNoteClue.front }} <i>✦</i></span>
          <span v-else>{{ tapeNoteClue.back }}</span>
        </button>
      </div>
      <div class="board-bottomline">
        <span>5 RECORDS PINNED</span><span>THREADS ARE ONLY A THEORY</span
        ><span>FIELD OFFICE // 1987?</span>
      </div>
    </section>

    <BoardMemberFileModal
      :member="activeIndex === null ? null : (members[activeIndex] ?? null)"
      :index="activeIndex ?? 0"
      :sigil="triangle"
      @close="closeMember"
    />
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { boardMembers as members } from '../data/teamBoardMembers'
import { pinnedBoardNotes as pinnedNotes, tapeNoteClue } from '../data/boardNotes'
import { useBoardPreparation } from '../composables/useBoardPreparation'
import { useStaticNoise } from '../../../composables/useStaticNoise'
import BoardJournalLayer from '../components/BoardJournalLayer.vue'
import BoardMemberFileModal from '../components/BoardMemberFileModal.vue'
import {
  AUDIO_ENABLED,
  SEAL_SIGNAL_LABELS,
  SEAL_STAGE_RESET_MS,
  SEAL_TAP_WINDOW_MS,
  SEAL_TERMINAL_DELAY_MS,
  SEAL_VISUAL_RESET_MS,
} from '../data/tapSealConfig'
import triangle from '@/assets/triangle.jpg'

const activeIndex = ref<number | null>(null)
const router = useRouter()
const sealStage = ref(0)
const sealFading = ref(false)
const sealResetting = ref(false)
const resetVisualStage = ref(0)
const sealSignalLabel = computed(() => SEAL_SIGNAL_LABELS[sealStage.value] ?? '')
const sealSymbolStyle = { '--seal-symbol': `url(${triangle})` }
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)')
let sealTapCount = 0
let lastSealTapAt = 0
let sealResetTimer: number | undefined
let sealVisualResetTimer: number | undefined
let terminalNavigationTimer: number | undefined
let sealAudioContext: AudioContext | undefined
const { preparing, introTitle, introKicker, introCount, titleGlitch } = useBoardPreparation()

const noteRevealed = ref(false)
const evidenceRevealed = ref(false)
const {
  canvasRef: boardNoise,
  canvasStyle: boardNoiseStyle,
  start: startBoardNoise,
} = useStaticNoise({
  opacity: 0.32,
  mobileQuery: '(max-width: 680px)',
})

function openMember(index: number) {
  activeIndex.value = index
}
function closeMember() {
  activeIndex.value = null
}
function onKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape' && activeIndex.value !== null) closeMember()
}
function resetSealSequence() {
  resetVisualStage.value = sealStage.value
  sealResetting.value = true
  sealTapCount = 0
  lastSealTapAt = 0
  sealStage.value = 0
  sealFading.value = false
  if (sealVisualResetTimer) clearTimeout(sealVisualResetTimer)
  sealVisualResetTimer = window.setTimeout(() => {
    sealResetting.value = false
    resetVisualStage.value = 0
  }, SEAL_VISUAL_RESET_MS)
}
function playSealAudio(stage: number) {
  if (!AUDIO_ENABLED || reducedMotion.matches) return
  try {
    const AudioContextConstructor =
      window.AudioContext ??
      (window as Window & { webkitAudioContext?: typeof AudioContext }).webkitAudioContext
    if (!AudioContextConstructor) return
    sealAudioContext ??= new AudioContextConstructor()
    void sealAudioContext.resume().catch(() => undefined)

    const context = sealAudioContext
    const gain = context.createGain()
    gain.gain.setValueAtTime(0.0001, context.currentTime)
    gain.gain.exponentialRampToValueAtTime(0.09, context.currentTime + 0.012)
    gain.gain.exponentialRampToValueAtTime(
      0.0001,
      context.currentTime + (stage === 5 ? 0.18 : 0.11),
    )
    gain.connect(context.destination)

    if (stage === 5) {
      const length = Math.floor(context.sampleRate * 0.16)
      const buffer = context.createBuffer(1, length, context.sampleRate)
      const samples = buffer.getChannelData(0)
      for (let index = 0; index < length; index += 1) samples[index] = Math.random() * 2 - 1
      const noise = context.createBufferSource()
      noise.buffer = buffer
      noise.connect(gain)
      noise.start()
      return
    }

    const oscillator = context.createOscillator()
    oscillator.type = 'square'
    oscillator.frequency.setValueAtTime(260 + stage * 115, context.currentTime)
    oscillator.connect(gain)
    oscillator.start()
    oscillator.stop(context.currentTime + 0.12)
  } catch {
    // Audio is an optional enhancement; unsupported or blocked audio stays silent.
  }
}
function vibrateSeal(stage: number) {
  if (reducedMotion.matches || typeof navigator.vibrate !== 'function') return
  if (navigator.userActivation && !navigator.userActivation.isActive) return
  const pattern: VibratePattern = stage <= 3 ? 20 : stage === 4 ? [40, 30, 80] : 200
  try {
    navigator.vibrate(pattern)
  } catch {
    // Vibration is optional and may be blocked by the device.
  }
}
function advanceSeal(event: PointerEvent) {
  if (preparing.value || sealStage.value === 5 || !event.isPrimary) return
  if (event.pointerType === 'mouse' && event.button !== 0) return
  if (sealVisualResetTimer) clearTimeout(sealVisualResetTimer)
  sealResetting.value = false
  resetVisualStage.value = 0

  const now = Date.now()
  if (now - lastSealTapAt > SEAL_TAP_WINDOW_MS) sealTapCount = 0
  lastSealTapAt = now
  sealTapCount += 1
  const nextStage = sealTapCount

  if (sealResetTimer) clearTimeout(sealResetTimer)
  if (nextStage < 5) {
    sealStage.value = nextStage
    playSealAudio(nextStage)
    vibrateSeal(nextStage)
    sealResetTimer = window.setTimeout(resetSealSequence, SEAL_STAGE_RESET_MS)
    return
  }

  sealStage.value = 5
  sealTapCount = 0
  sealResetting.value = false
  resetVisualStage.value = 0
  if (reducedMotion.matches) sealFading.value = true
  playSealAudio(5)
  vibrateSeal(5)
  terminalNavigationTimer = window.setTimeout(
    () => {
      sealStage.value = 0
      void router.push('/terminal')
    },
    reducedMotion.matches ? 220 : SEAL_TERMINAL_DELAY_MS,
  )
}
onMounted(() => {
  window.addEventListener('keydown', onKeydown)
  startBoardNoise()
})
onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
  if (sealResetTimer) clearTimeout(sealResetTimer)
  if (sealVisualResetTimer) clearTimeout(sealVisualResetTimer)
  if (terminalNavigationTimer) clearTimeout(terminalNavigationTimer)
  if (sealAudioContext && sealAudioContext.state !== 'closed') void sealAudioContext.close()
})
</script>

<style scoped src="./TeamInvestigationBoardPage.css"></style>
