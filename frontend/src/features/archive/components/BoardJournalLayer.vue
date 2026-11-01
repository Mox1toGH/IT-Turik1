<template>
  <div ref="layer" class="journal-layer" :class="{ 'is-glitching': glitching }" aria-hidden="true">
    <div class="journal-uv">
      <svg class="journal-svg revealed-svg" viewBox="0 0 1200 690" preserveAspectRatio="none">
        <g class="uv-ink">
          <path d="M600 345 0 300M600 345 1200 292M600 345 100 650M600 345 1090 660" />
          <path d="M315 110A420 420 0 0 1 885 110M235 195A520 520 0 0 0 965 195" />
          <text
            v-for="note in uvBoardNotes"
            :key="note.id"
            :x="note.x"
            :y="note.y"
            :class="['uv-note', note.hand, { 'note-struck': note.struck }]"
            :transform="`rotate(${note.rotation} ${note.x} ${note.y})`"
          >
            {{ note.text }}
          </text>
          <path d="m330 125 17-18 17 18-17 18zM852 541l13-23 13 23zM180 525h28m-14-14v28" />
          <circle cx="600" cy="345" r="18" />
          <circle cx="600" cy="345" r="28" />
        </g>
      </svg>
    </div>

    <svg class="journal-svg base-svg" viewBox="0 0 1200 690" preserveAspectRatio="none">
      <defs>
        <filter id="ink-wobble" x="-5%" y="-5%" width="110%" height="110%">
          <feTurbulence
            type="fractalNoise"
            baseFrequency=".018"
            numOctaves="1"
            seed="8"
            result="noise"
          />
          <feDisplacementMap
            in="SourceGraphic"
            in2="noise"
            scale="1.8"
            xChannelSelector="R"
            yChannelSelector="G"
          />
        </filter>
        <path id="cipher-ring" d="M 325,345 a 275,275 0 1,1 550,0 a 275,275 0 1,1 -550,0" />
        <g id="sigil-a">
          <path d="M0-12 9 7H-9Z M0-12v23" />
          <circle cy="2" r="2" />
        </g>
        <g id="sigil-b"><path d="M-11 0a11 11 0 0 1 22 0M0-11v22m-8 0 8-6 8 6" /></g>
        <g id="sigil-c">
          <path d="M-10-8h20L0 10zM-5-8 5 8" />
          <circle cy="-2" r="1.5" />
        </g>
      </defs>
      <g class="paper-marks">
        <circle cx="165" cy="156" r="52" />
        <circle cx="165" cy="156" r="45" class="ring-break" />
        <circle cx="1030" cy="530" r="63" />
        <circle cx="1030" cy="530" r="55" class="ring-break" />
        <path d="M0 38q88 20 120 0M1080 0q22 48 120 30M0 650q74-35 130 5M1080 690q40-40 120-27" />
        <path
          class="torn"
          d="m75 222 65-11 18 14-5 38-70 9-18-22zM1030 200l92-13 16 18-12 31-80 8-21-17z"
        />
      </g>

      <g class="main-ink" filter="url(#ink-wobble)">
        <circle class="orbit orbit-one" cx="600" cy="345" r="292" />
        <circle class="orbit orbit-two" cx="600" cy="345" r="315" />
        <circle class="orbit orbit-three" cx="600" cy="345" r="337" />
        <text class="cipher-ring">
          <textPath href="#cipher-ring">
            TRIANGULUM VIGILAT · TRIANGULUM VIGILAT · TRIANGULUM VIGILAT · TRIANGULUM VIGILAT ·
          </textPath>
        </text>
        <g class="sigil-ring">
          <use href="#sigil-a" transform="translate(600 15)" />
          <use href="#sigil-b" transform="translate(765 58) rotate(30)" />
          <use href="#sigil-c" transform="translate(900 175) rotate(60)" />
          <use href="#sigil-a" transform="translate(935 345) rotate(90)" />
          <use href="#sigil-b" transform="translate(900 515) rotate(120)" />
          <use href="#sigil-c" transform="translate(765 632) rotate(150)" />
          <use href="#sigil-a" transform="translate(600 675) rotate(180)" />
          <use href="#sigil-b" transform="translate(435 632) rotate(210)" />
          <use href="#sigil-c" transform="translate(300 515) rotate(240)" />
          <use href="#sigil-a" transform="translate(265 345) rotate(270)" />
          <use href="#sigil-b" transform="translate(300 175) rotate(300)" />
          <use href="#sigil-c" transform="translate(435 58) rotate(330)" />
        </g>
        <g class="rays">
          <path
            d="M600 345 20 75M600 345 1180 72M600 345 10 470M600 345 1190 475M600 345 170 685M600 345 1030 685"
          />
        </g>
        <g class="great-mark">
          <path class="triangle retrace" d="M600 62 280 610 920 610 M600 62 916 607" />
          <path class="triangle" d="M600 66 284 606 914 606" />
          <path class="inner-mark" d="M600 286 651 345 600 404 549 345Z" />
          <path class="inner-mark" d="M600 286v320" />
          <path class="eye-lid" d="M577 345q23-20 46 0-23 19-46 0z" />
          <path class="eye-pupil" d="M600 336v17" />
          <path
            class="eye-ray"
            d="M538 345h-36m160 0h36M545 332l-18-12m128 12 18-12M545 358l-18 12m128-12 18 12"
          />
          <path class="stem" d="M600 404v201m0 0-14 18m14-18 14 18" />
        </g>
        <g class="small-marks">
          <g transform="translate(164 335) rotate(-17) scale(.55)">
            <path d="M0-35 31 20h-62zM0-35v65" />
            <path class="crossout" d="m-40-38 82 75m-76 6 70-86" />
          </g>
          <g transform="translate(1045 335) rotate(14) scale(.48)">
            <path d="M0-35 31 20h-62zM0-35v65" />
          </g>
          <g transform="translate(180 570) rotate(26) scale(.38)">
            <path d="M0-35 31 20h-62zM0-35v65" />
          </g>
          <g transform="translate(1020 120) rotate(-31) scale(.34)">
            <path d="M0-35 31 20h-62zM0-35v65" />
            <path class="crossout" d="m-38 28 76-56" />
          </g>
        </g>
      </g>

      <g class="notes">
        <text
          v-for="note in boardNotes"
          :key="note.id"
          :x="note.x"
          :y="note.y"
          :class="['note', note.hand, { 'note-struck': note.struck }]"
          :transform="`rotate(${note.rotation} ${note.x} ${note.y})`"
        >
          {{ note.text }}
        </text>
      </g>
    </svg>

    <button
      class="eye-hit"
      type="button"
      tabindex="-1"
      aria-label="Open the field computer"
      @click="enterComputer"
    ></button>
    <div v-if="glitching" class="entrance-glitch"></div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { boardNotes, uvBoardNotes } from '../data/boardNotes'

const router = useRouter()
const layer = ref<HTMLElement | null>(null)
const glitching = ref(false)
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)')

let animationFrame = 0
let blinkTimer: ReturnType<typeof setTimeout> | undefined
let pupilX = 0
let pupilY = 0

function trackPointer(event: PointerEvent) {
  const element = layer.value
  if (!element || reducedMotion.matches) return

  const bounds = element.getBoundingClientRect()
  const x = ((event.clientX - bounds.left) / bounds.width) * 1200
  const y = ((event.clientY - bounds.top) / bounds.height) * 690

  if (animationFrame) cancelAnimationFrame(animationFrame)
  animationFrame = requestAnimationFrame(() => {
    pupilX = Math.max(-2.5, Math.min(2.5, (x - 600) / 180))
    pupilY = Math.max(-2.5, Math.min(2.5, (y - 345) / 140))
    element.style.setProperty('--pupil-x', `${pupilX}px`)
    element.style.setProperty('--pupil-y', `${pupilY}px`)
  })
}

function scheduleBlink() {
  if (reducedMotion.matches) return

  blinkTimer = setTimeout(
    () => {
      layer.value?.classList.add('eye-blink')
      setTimeout(() => layer.value?.classList.remove('eye-blink'), 150)
      scheduleBlink()
    },
    20000 + Math.random() * 20000,
  )
}

async function enterComputer() {
  if (glitching.value) return

  if (reducedMotion.matches) {
    await router.push('/terminal')
    return
  }

  glitching.value = true
  window.setTimeout(() => void router.push('/terminal'), 380)
}

onMounted(() => {
  scheduleBlink()
  window.addEventListener('pointermove', trackPointer, { passive: true })
  window.addEventListener('pointerdown', trackPointer, { passive: true })
})

onUnmounted(() => {
  if (blinkTimer) clearTimeout(blinkTimer)
  if (animationFrame) cancelAnimationFrame(animationFrame)

  window.removeEventListener('pointermove', trackPointer)
  window.removeEventListener('pointerdown', trackPointer)
})
</script>

<style scoped>
.journal-layer {
  position: absolute;
  z-index: 0;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  color: #39291d;
  --pupil-x: 0px;
  --pupil-y: 0px;
}
.journal-svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}
.base-svg {
  opacity: 0.86;
}
.paper-marks {
  fill: none;
  stroke: #4d3022;
  stroke-width: 2.3;
  opacity: 0.13;
}
.paper-marks .ring-break {
  stroke-dasharray: 145 24 75 42;
  stroke-width: 4;
}
.paper-marks .torn {
  fill: #cfb887;
  stroke: #402b1d;
  stroke-width: 1.4;
  opacity: 0.2;
}
.main-ink {
  fill: none;
  stroke: #38291f;
  stroke-width: 2.5;
  stroke-linecap: round;
  stroke-linejoin: round;
  opacity: 0.18;
  mix-blend-mode: multiply;
}
.orbit {
  stroke-width: 1.5;
}
.orbit-two {
  stroke-dasharray: 4 8;
}
.orbit-three {
  stroke-dasharray: 1 11;
}
.cipher-ring {
  fill: #34271e;
  stroke: none;
  font:
    12px 'Special Elite',
    ui-monospace,
    monospace;
  letter-spacing: 5px;
  opacity: 0.8;
}
.sigil-ring {
  stroke-width: 2.5;
}
.sigil-ring use {
  fill: none;
}
.rays {
  stroke-width: 1.5;
  stroke-dasharray: 2 6;
  opacity: 0.72;
}
.great-mark {
  stroke-width: 4;
}
.triangle {
  stroke-width: 4.5;
}
.retrace {
  transform: translate(3px, -2px);
  opacity: 0.48;
  stroke-width: 2;
}
.inner-mark {
  stroke-width: 3;
}
.eye-lid {
  fill: #38291f;
  stroke-width: 2;
}
.eye-pupil {
  transform: translate(var(--pupil-x), var(--pupil-y));
  stroke-width: 4;
  transition: transform 120ms ease-out;
}
.eye-ray {
  stroke-width: 3;
}
.stem {
  stroke-width: 3;
}
.small-marks {
  stroke-width: 4;
}
.crossout {
  stroke: #794039;
  stroke-width: 5;
  opacity: 0.8;
}
.notes {
  fill: #352a22;
  stroke: none;
  opacity: 0.64;
}
.hand {
  font:
    22px 'Caveat',
    cursive;
}
.hand-one {
  fill: #39291f;
}
.hand-two {
  font:
    23px 'Reenie Beanie',
    cursive;
  fill: #38424a;
}
.hand-three {
  font-size: 21px;
  fill: #793e35;
}
.typed {
  font:
    11px 'Special Elite',
    ui-monospace,
    monospace;
  letter-spacing: 1px;
  fill: #37404a;
}
.small-note {
  font-size: 10px;
  fill: #78443c;
}
.strike {
  stroke: #753b32;
  stroke-width: 2;
  opacity: 0.65;
}
.note-struck {
  text-decoration: line-through;
}
.journal-uv {
  position: absolute;
  inset: 0;
  opacity: 0.34;
}
.revealed-svg {
  color: #bd9b55;
}
.uv-ink {
  fill: none;
  stroke: #d7bd78;
  stroke-width: 2.2;
  stroke-linecap: round;
  opacity: 0.92;
  filter: drop-shadow(0 0 3px rgba(218, 187, 103, 0.45));
}
.uv-ink text {
  fill: #e1cc8d;
  stroke: none;
  font:
    13px 'Special Elite',
    ui-monospace,
    monospace;
  letter-spacing: 2px;
}
.uv-ink .uv-note {
  font-size: 13px;
  letter-spacing: 1.5px;
}
.uv-ink .hand {
  font-family: 'Caveat', cursive;
  font-size: 20px;
}
.uv-ink .hand-two {
  font-family: 'Reenie Beanie', cursive;
  font-size: 22px;
}
.uv-ink .hand-three {
  font-family: 'Caveat', cursive;
  font-size: 19px;
}
.eye-hit {
  position: absolute;
  pointer-events: auto;
  left: 50%;
  top: 50%;
  width: 5%;
  height: 6%;
  min-width: 30px;
  min-height: 24px;
  transform: translate(-50%, -50%);
  border: 0;
  padding: 0;
  background: transparent;
  cursor: crosshair;
  opacity: 0.015;
}
.eye-hit:focus-visible {
  outline: 1px dotted rgba(55, 38, 24, 0.4);
  outline-offset: 2px;
}
.eye-blink .eye-lid {
  transform: scaleY(0.05);
  transform-origin: center;
  transition: transform 70ms;
}
.eye-blink .eye-pupil {
  opacity: 0;
}
.entrance-glitch {
  position: absolute;
  inset: 0;
  z-index: 5;
  background: repeating-linear-gradient(0deg, rgba(40, 30, 24, 0.28) 0 2px, transparent 2px 5px);
  animation: glitch-in 0.38s steps(4) both;
}
.is-glitching .base-svg {
  filter: contrast(1.7) brightness(0.65);
}
@keyframes glitch-in {
  0% {
    opacity: 0;
    clip-path: inset(45% 0 48%);
  }
  25% {
    opacity: 0.8;
    clip-path: inset(15% 0 68%);
  }
  60% {
    opacity: 0.55;
    clip-path: inset(70% 0 12%);
  }
  100% {
    opacity: 0.9;
    clip-path: inset(0);
  }
}
@media (max-width: 680px) {
  .journal-layer {
    opacity: 0.82;
  }
  .small-marks {
    display: none;
  }
  .notes {
    opacity: 0.5;
  }
  .cipher-ring {
    font-size: 10px;
    letter-spacing: 3px;
  }
  .journal-uv {
    opacity: 0.3;
  }
  .eye-hit {
    width: 8%;
    height: 7%;
    top: 50%;
  }
}
@media (prefers-reduced-motion: reduce) {
  .entrance-glitch {
    animation: none;
  }
  .eye-hit {
    cursor: pointer;
  }
}
</style>
