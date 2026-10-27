<template>
  <Transition name="file-modal">
    <div v-if="member" class="file-overlay" @click.self="emit('close')">
      <section
        class="file-modal"
        role="dialog"
        aria-modal="true"
        :aria-labelledby="`modal-name-${index}`"
      >
        <button
          ref="closeButton"
          class="modal-close"
          type="button"
          aria-label="Close personnel file"
          @click="emit('close')"
        >
          ×
        </button>
        <div class="modal-topline">
          <span>FIELD OFFICE / PERSONNEL NOTE</span>
        </div>
        <div class="modal-content">
          <div class="modal-photo">
            <img
              v-if="member.photo"
              class="member-photo-image"
              :src="member.photo"
              :alt="member.name"
            />
            <img v-else :src="sigil" alt="" />
            <template v-if="!member.photo"
              ><span>{{ member.photoMark }}</span
              ><small>PHOTO NOT ON FILE</small></template
            >
          </div>
          <div class="modal-copy">
            <span class="modal-kicker">SUBJECT IDENTIFIED · {{ member.kind }}</span>
            <h2 :id="`modal-name-${index}`">{{ member.name }}</h2>
            <p class="modal-role">{{ member.role }}</p>
            <p class="modal-description">{{ member.description }}</p>
            <div class="modal-focus">
              <span>AREA OF INVOLVEMENT</span><b>{{ member.focus }}</b>
            </div>
            <div class="modal-socials">
              <span>CONTACT CLUES</span>
              <div class="modal-member-links">
                <a
                  v-for="link in member.links"
                  :key="link.href"
                  :href="link.href"
                  :aria-label="link.icon.title"
                  :title="link.icon.title"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <svg viewBox="0 0 24 24" aria-hidden="true"><path :d="link.icon.path" /></svg>
                  <span>{{ link.icon.title }}</span>
                </a>
                <small v-if="!member.links.length">NO CONTACT CLUES ON FILE</small>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-bottom">
          <span>CASE COPY · DO NOT CIRCULATE</span
          ><button type="button" @click="emit('close')">PUT IT BACK ON THE BOARD ↵</button>
        </div>
      </section>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { nextTick, onUnmounted, ref, watch } from 'vue'
import type { BoardMember } from '../data/teamBoardMembers'

interface Props {
  member: BoardMember | null
  index: number
  sigil: string
}

interface Emits {
  close: []
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const closeButton = ref<HTMLButtonElement | null>(null)
let returnFocus: HTMLElement | null = null

watch(
  () => props.member,
  (member) => {
    if (member) {
      returnFocus = document.activeElement instanceof HTMLElement ? document.activeElement : null
      nextTick(() => closeButton.value?.focus())
    } else {
      nextTick(() => returnFocus?.focus())
    }
  },
)

onUnmounted(() => {
  if (returnFocus?.isConnected) returnFocus.focus()
})
</script>

<style scoped>
.file-overlay {
  position: fixed;
  z-index: 30;
  inset: 0;
  display: grid;
  place-items: center;
  padding: 20px;
  background: rgba(11, 13, 11, 0.78);
  backdrop-filter: blur(3px);
}
.file-modal {
  position: relative;
  width: min(760px, 100%);
  max-height: min(90svh, 760px);
  overflow: auto;
  padding: 22px 25px 17px;
  border: 10px solid #40382b;
  background: #dfd4ae;
  box-shadow: 0 25px 100px #000;
  color: #3e382c;
}
.file-modal::before {
  position: absolute;
  inset: 4px;
  border: 1px solid rgba(106, 83, 49, 0.5);
  content: '';
  pointer-events: none;
}
.modal-close {
  position: absolute;
  z-index: 2;
  top: 8px;
  right: 11px;
  border: 0;
  background: none;
  color: #784137;
  font:
    22px Georgia,
    serif;
  cursor: pointer;
}
.modal-topline,
.modal-bottom {
  position: relative;
  display: flex;
  justify-content: space-between;
  gap: 14px;
  color: #796a4b;
  font:
    10px ui-monospace,
    monospace;
  letter-spacing: 0.13em;
}
.modal-content {
  position: relative;
  display: grid;
  grid-template-columns: 0.8fr 1.2fr;
  gap: 28px;
  align-items: center;
  padding: 24px 0;
}
.modal-photo {
  position: relative;
  min-height: 265px;
  display: grid;
  place-items: center;
  overflow: hidden;
  border: 1px solid #95845e;
  background: #beb38b;
  text-align: center;
}
.modal-photo img {
  position: absolute;
  width: 80%;
  height: 80%;
  object-fit: contain;
  mix-blend-mode: multiply;
  opacity: 0.15;
}
.modal-photo img.member-photo-image {
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
  mix-blend-mode: normal;
  opacity: 1;
}
.modal-photo > span,
.modal-photo > small,
.modal-photo > i {
  position: relative;
}
.modal-photo > span {
  color: #6f6042;
  font-size: 34px;
}
.modal-photo > small {
  color: #716547;
  font:
    10px ui-monospace,
    monospace;
}
.modal-photo > i {
  position: absolute;
  top: 8px;
  left: 9px;
  color: #994237;
  font:
    10px ui-monospace,
    monospace;
}
.modal-kicker {
  color: #a45238;
  font:
    10px ui-monospace,
    monospace;
  letter-spacing: 0.1em;
}
.modal-copy h2 {
  margin: 10px 0 5px;
  font-size: clamp(24px, 4vw, 38px);
  font-weight: 400;
  line-height: 1.02;
}
.modal-role {
  margin: 0;
  color: #6c6149;
  font-size: 12px;
}
.modal-description {
  margin: 17px 0;
  color: #5d533d;
  font-size: 13px;
  line-height: 1.6;
}
.modal-focus,
.modal-socials {
  padding-top: 11px;
  border-top: 1px dashed #a3926a;
}
.modal-focus span,
.modal-socials > span {
  display: block;
  margin-bottom: 5px;
  color: #85744f;
  font:
    10px ui-monospace,
    monospace;
  letter-spacing: 0.1em;
}
.modal-focus b {
  font-size: 11px;
  font-weight: 400;
}
.modal-socials {
  margin-top: 12px;
}
.modal-socials > div {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.modal-member-links a {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  color: #5e563f;
  font:
    10px ui-monospace,
    monospace;
  text-decoration: none;
}
.modal-member-links svg {
  width: 15px;
  height: 15px;
  flex: 0 0 auto;
  fill: currentColor;
}
.modal-member-links a:hover {
  color: #a45238;
}
.modal-member-links > small {
  color: #9c5940;
  font-size: 10px;
}
.modal-bottom {
  padding-top: 12px;
  border-top: 1px solid #a3926a;
  align-items: center;
}
.modal-bottom button {
  border: 0;
  background: none;
  color: #8d4134;
  font:
    10px ui-monospace,
    monospace;
  letter-spacing: 0.06em;
  cursor: pointer;
}
.modal-bottom button:hover {
  color: #b4573e;
}
.modal-close:focus-visible,
.modal-bottom button:focus-visible {
  outline: 2px solid #812f28;
  outline-offset: 3px;
}
.file-modal-enter-active,
.file-modal-leave-active {
  transition:
    opacity 0.2s,
    transform 0.25s;
}
.file-modal-enter-from,
.file-modal-leave-to {
  opacity: 0;
}
.file-modal-enter-from .file-modal,
.file-modal-leave-to .file-modal {
  transform: translateY(9px) rotate(-0.4deg);
}
@media (max-width: 680px) {
  .file-overlay {
    padding: 12px;
  }
  .file-modal {
    padding: 20px 15px 13px;
    border-width: 7px;
  }
  .modal-content {
    grid-template-columns: 1fr;
    gap: 14px;
    padding: 17px 0;
  }
  .modal-photo {
    min-height: 170px;
  }
  .modal-description {
    font-size: 12px;
  }
  .modal-topline,
  .modal-bottom {
    font-size: 9px;
  }
  .modal-bottom button {
    font-size: 9px;
  }
}
@media (max-height: 680px) {
  .file-overlay {
    padding: 8px;
  }
  .file-modal {
    max-height: 96svh;
    padding-top: 14px;
    padding-bottom: 12px;
  }
  .modal-content {
    gap: 14px;
    padding-top: 12px;
    padding-bottom: 12px;
  }
  .modal-photo {
    height: min(34svh, 210px);
    min-height: 0;
  }
  .modal-photo img.member-photo-image {
    object-fit: contain;
  }
  .modal-description {
    margin-top: 9px;
    margin-bottom: 9px;
  }
  .modal-focus,
  .modal-socials {
    padding-top: 7px;
  }
  .modal-socials {
    margin-top: 7px;
  }
}
@media (max-width: 680px) and (max-height: 680px) {
  .modal-content {
    grid-template-columns: 1fr;
    gap: 9px;
    padding-top: 9px;
    padding-bottom: 9px;
  }
  .modal-photo {
    height: min(25svh, 150px);
    min-height: 90px;
  }
}
@media (prefers-reduced-motion: reduce) {
  .file-modal-enter-active,
  .file-modal-leave-active {
    transition: none;
  }
}
</style>
