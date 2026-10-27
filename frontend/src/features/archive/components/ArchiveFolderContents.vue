<template>
  <section class="folder-content">
    <div class="folder-toolbar">
      <button type="button" class="archive-back" @click="emit('back')">← INDEX</button>
      <p>
        {{ folder.description }} <span>// {{ folder.files.length }} ENTRIES</span>
      </p>
    </div>
    <div class="archive-photo-grid">
      <button
        v-for="file in folder.files"
        :key="file.id"
        type="button"
        class="photo-file"
        :class="{ corrupted: file.corrupted }"
        @click="emit('open-file', file)"
      >
        <span class="photo-thumb">
          <img :src="file.thumb" alt="" loading="lazy" decoding="async" />
          <span v-if="file.corrupted" class="corrupt-stamp">CORRUPTED</span>
          <i class="thumb-scanlines"></i>
        </span>
        <span class="photo-file-name">{{ file.filename }}</span>
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
import type { ArchiveFolder, ArchivePhotoFile } from '../data/foundArchive'

interface Props {
  folder: ArchiveFolder
}

interface Emits {
  back: []
  'open-file': [file: ArchivePhotoFile]
}

defineProps<Props>()
const emit = defineEmits<Emits>()
</script>

<style scoped>
.folder-content {
  min-height: 100%;
  padding: clamp(14px, 2vw, 26px);
}
.folder-toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 14px;
  border-bottom: 1px solid rgba(145, 169, 105, 0.28);
  padding-bottom: 10px;
  color: #aabb82;
  font-size: 13px;
  letter-spacing: 0.06em;
}
.folder-toolbar p {
  margin: 0;
}
.folder-toolbar p span {
  color: #74865d;
}
.archive-back {
  border: 1px solid #60764b;
  background: #1b281b;
  color: #e5edcf;
  padding: 7px 10px;
  font: inherit;
  font-size: 12px;
  letter-spacing: 0.06em;
  cursor: pointer;
  text-shadow: 0 0 5px rgba(185, 218, 142, 0.28);
}
.archive-back:hover,
.archive-back:focus-visible {
  background: #2d4028;
  color: #f4f4dc;
  outline: 1px solid #a1b975;
  outline-offset: 2px;
}
.archive-photo-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12px;
}
.photo-file {
  display: grid;
  align-content: start;
  min-width: 0;
  padding: 7px;
  border: 1px solid rgba(120, 146, 83, 0.26);
  background: rgba(7, 16, 9, 0.52);
  color: #c3d19c;
  text-align: left;
  font: inherit;
  cursor: pointer;
  transition:
    border-color 0.18s,
    background 0.18s;
}
.photo-file:hover,
.photo-file:focus-visible {
  border-color: #abc77a;
  background: rgba(58, 76, 43, 0.34);
  outline: none;
}
.photo-thumb {
  position: relative;
  display: block;
  overflow: hidden;
  aspect-ratio: 4 / 3;
  background: #172019;
}
.photo-thumb img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
}
.photo-file.corrupted .photo-thumb img {
  filter: hue-rotate(78deg) contrast(1.4) saturate(1.8);
  transform: skewX(-2deg);
}
.thumb-scanlines {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: repeating-linear-gradient(0deg, transparent 0 3px, rgba(4, 10, 5, 0.3) 4px);
}
.corrupt-stamp,
.lock-stamp {
  position: absolute;
  top: 8px;
  left: 5px;
  padding: 3px 5px;
  background: rgba(28, 8, 6, 0.85);
  color: #e28b68;
  font-size: 10px;
  letter-spacing: 0.1em;
  transform: rotate(-7deg);
}
.lock-stamp {
  color: #ccd79b;
  background: rgba(5, 13, 8, 0.86);
}
.photo-file-name {
  overflow: hidden;
  margin-top: 7px;
  font-size: clamp(12px, 0.95vw, 14px);
  text-overflow: ellipsis;
  white-space: nowrap;
}
.sealed-note {
  color: #a1ad80;
  font-size: 12px;
  text-align: center;
  letter-spacing: 0.12em;
}
@media (min-width: 1100px) {
  .archive-photo-grid {
    grid-template-columns: repeat(6, minmax(0, 1fr));
  }
}
@media (max-width: 760px) {
  .folder-content {
    padding: 14px 12px;
  }
  .folder-toolbar {
    align-items: flex-start;
    flex-direction: column;
    gap: 8px;
  }
  .archive-photo-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
  }
  .photo-file-name {
    font-size: 13px;
  }
}
</style>
