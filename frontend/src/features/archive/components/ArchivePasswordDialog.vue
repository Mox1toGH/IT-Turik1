<template>
  <div class="password-layer" role="presentation" @click.self="emit('close')">
    <form
      class="password-dialog"
      role="dialog"
      aria-modal="true"
      aria-labelledby="password-title"
      @submit.prevent="emit('submit', password)"
    >
      <button class="dialog-close" type="button" aria-label="Close" @click="emit('close')">
        ×
      </button>
      <span class="dialog-classification">AUTHENTICATION REQUIRED</span>
      <h2 id="password-title">{{ file.filename }}</h2>
      <p>RECOVERY KEY REQUIRED TO REPAIR THIS RECORD.</p>
      <label for="archive-password">ARCHIVE PASSWORD</label>
      <input
        id="archive-password"
        v-model="password"
        type="password"
        autocomplete="off"
        autofocus
      />
      <p v-if="error" class="password-error" role="alert">{{ error }}</p>
      <button type="submit">ATTEMPT RECOVERY ↵</button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { ArchivePhotoFile } from '../data/foundArchive'

interface Props {
  file: ArchivePhotoFile
  error: string
}

interface Emits {
  close: []
  submit: [password: string]
}

defineProps<Props>()

const emit = defineEmits<Emits>()
const password = ref('')
</script>

<style scoped>
.password-layer {
  position: absolute;
  z-index: 8;
  inset: 0;
  display: grid;
  place-items: center;
  overflow: auto;
  padding: 14px;
  background: rgba(1, 5, 2, 0.91);
  backdrop-filter: blur(3px);
}
.password-dialog {
  position: relative;
  width: min(420px, 100%);
  padding: 24px;
  border: 1px solid rgba(157, 186, 111, 0.58);
  background: #101b11;
  color: #cad9a5;
  box-shadow: 0 0 30px rgba(123, 159, 72, 0.14);
}
.password-dialog h2 {
  margin: 10px 0;
  font-size: 17px;
}
.password-dialog p {
  color: #95a47b;
  font-size: 12px;
  line-height: 1.5;
}
.dialog-classification,
.password-dialog label {
  color: #9eb678;
  font-size: 10px;
  letter-spacing: 0.14em;
}
.password-dialog label {
  display: block;
  margin: 18px 0 6px;
}
.password-dialog input {
  box-sizing: border-box;
  width: 100%;
  padding: 11px;
  border: 1px solid #62784d;
  background: #080f09;
  color: #d2e8ad;
  font: inherit;
}
.password-dialog > button[type='submit'] {
  margin-top: 12px;
  padding: 10px 12px;
  border: 1px solid #829b5e;
  background: #283a25;
  color: #d2e4aa;
  font: inherit;
  font-size: 12px;
  cursor: pointer;
}
.dialog-close {
  position: absolute;
  top: 7px;
  right: 9px;
  border: 0;
  background: none;
  color: #b3c48f;
  font-size: 20px;
  cursor: pointer;
}
.password-error {
  color: #e38c6e !important;
}
</style>
