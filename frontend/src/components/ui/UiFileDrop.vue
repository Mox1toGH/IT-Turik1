<template>
  <div class="file-drop" :class="{ 'has-error': !!errorMessage }">
    <div
      class="dropzone"
      :class="{ 'is-dragging': isDragging, 'is-disabled': disabled }"
      role="button"
      tabindex="0"
      :aria-disabled="disabled"
      @click="handleZoneClick"
      @keydown.enter.prevent="handleZoneClick"
      @keydown.space.prevent="handleZoneClick"
      @dragenter.prevent="onDragEnter"
      @dragover.prevent="onDragOver"
      @dragleave.prevent="onDragLeave"
      @drop.prevent="onDrop"
    >
      <VisuallyHidden as-child>
        <input
          :id="inputId"
          ref="inputRef"
          type="file"
          :accept="accept"
          :multiple="multiple"
          :disabled="disabled"
          @change="onInputChange"
          @click="(e) => e.stopPropagation()"
        />
      </VisuallyHidden>

      <div class="dropzone-icon" aria-hidden="true">
        <svg
          viewBox="0 0 24 24"
          width="28"
          height="28"
          fill="none"
          stroke="currentColor"
          stroke-width="1.6"
        >
          <path d="M12 16V4" stroke-linecap="round" stroke-linejoin="round" />
          <path d="M7 9l5-5 5 5" stroke-linecap="round" stroke-linejoin="round" />
          <path
            d="M4 16v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
      </div>

      <p class="dropzone-title"><span class="link-text">Click to upload</span> or drag and drop</p>
      <p class="dropzone-hint">{{ hintText }}</p>
    </div>

    <p v-if="errorMessage" class="text-error file-drop-error">{{ errorMessage }}</p>

    <ul v-if="files.length" class="file-list">
      <li v-for="entry in files" :key="entry.id" class="file-row">
        <div class="file-thumb">
          <img v-if="entry.previewUrl" :src="entry.previewUrl" alt="" />
          <svg
            v-else
            viewBox="0 0 24 24"
            width="18"
            height="18"
            fill="none"
            stroke="currentColor"
            stroke-width="1.6"
          >
            <path
              d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"
              stroke-linejoin="round"
            />
            <path d="M14 2v6h6" stroke-linejoin="round" />
          </svg>
        </div>

        <div class="file-meta">
          <p class="file-name" :title="entry.file.name">{{ truncateName(entry.file.name) }}</p>
          <p class="file-size">{{ formatBytes(entry.file.size) }}</p>
        </div>

        <button
          type="button"
          class="file-remove"
          aria-label="Remove file"
          @click="removeFile(entry.id)"
        >
          <svg
            viewBox="0 0 24 24"
            width="16"
            height="16"
            fill="none"
            stroke="currentColor"
            stroke-width="1.8"
          >
            <path d="M18 6 6 18M6 6l12 12" stroke-linecap="round" />
          </svg>
        </button>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, ref, useId, watch } from 'vue'
import { VisuallyHidden } from 'reka-ui'

interface FileEntry {
  id: string
  file: File
  previewUrl: string | null
}

interface Props {
  modelValue?: File[]
  accept?: string
  multiple?: boolean
  disabled?: boolean
  maxFiles?: number
  maxSizeMb?: number
  hint?: string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: () => [],
  accept: undefined,
  multiple: true,
  disabled: false,
  maxFiles: undefined,
  maxSizeMb: undefined,
  hint: undefined,
})

const emit = defineEmits<{
  'update:modelValue': [files: File[]]
  error: [message: string]
}>()

const inputId = useId()
const inputRef = ref<HTMLInputElement | null>(null)
const isDragging = ref(false)
const dragDepth = ref(0)
const errorMessage = ref('')

const files = ref<FileEntry[]>([])

function makeEntry(file: File): FileEntry {
  const isImage = file.type.startsWith('image/')
  return {
    id: `${file.name}-${file.size}-${file.lastModified}-${Math.random().toString(36).slice(2, 8)}`,
    file,
    previewUrl: isImage ? URL.createObjectURL(file) : null,
  }
}

function revoke(entry: FileEntry) {
  if (entry.previewUrl) URL.revokeObjectURL(entry.previewUrl)
}

watch(
  () => props.modelValue,
  (value) => {
    const incoming = value ?? []
    const known = new Set(files.value.map((entry) => entry.file))
    const same = incoming.length === files.value.length && incoming.every((file) => known.has(file))
    if (same) return

    files.value.forEach(revoke)
    files.value = incoming.map(makeEntry)
  },
  { immediate: true },
)

onBeforeUnmount(() => {
  files.value.forEach(revoke)
})

const hintText = computed(() => {
  if (props.hint) return props.hint
  const parts: string[] = []
  if (props.accept)
    parts.push(
      props.accept
        .split(',')
        .map((t) => t.trim())
        .join(', '),
    )
  if (props.maxSizeMb) parts.push(`up to ${props.maxSizeMb}MB`)
  if (props.maxFiles) parts.push(`max ${props.maxFiles} file${props.maxFiles === 1 ? '' : 's'}`)
  return parts.length ? parts.join(' \u2022 ') : 'Any file type'
})

function formatBytes(bytes: number) {
  if (bytes === 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  const exponent = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1)
  const value = bytes / 1024 ** exponent
  return `${exponent === 0 ? value : value.toFixed(1)} ${units[exponent]}`
}

function truncateName(name: string, max = 32) {
  if (name.length <= max) return name
  const dot = name.lastIndexOf('.')
  const ext = dot > -1 ? name.slice(dot) : ''
  const base = dot > -1 ? name.slice(0, dot) : name
  return `${base.slice(0, max - ext.length - 1)}\u2026${ext}`
}

function commit() {
  emit(
    'update:modelValue',
    files.value.map((entry) => entry.file),
  )
}

function setError(message: string) {
  errorMessage.value = message
  if (message) emit('error', message)
}

function validate(candidate: File): string | null {
  if (props.accept) {
    const patterns = props.accept.split(',').map((p) => p.trim().toLowerCase())
    const type = candidate.type.toLowerCase()
    const ext = `.${candidate.name.split('.').pop()?.toLowerCase()}`
    const matches = patterns.some((pattern) => {
      if (pattern.startsWith('.')) return ext === pattern
      if (pattern.endsWith('/*')) return type.startsWith(pattern.replace('/*', '/'))
      return type === pattern
    })
    if (!matches) return `"${candidate.name}" isn't an accepted file type.`
  }
  if (props.maxSizeMb && candidate.size > props.maxSizeMb * 1024 * 1024) {
    return `"${candidate.name}" is over the ${props.maxSizeMb}MB limit.`
  }
  return null
}

function addFiles(list: FileList | File[]) {
  if (props.disabled) return
  setError('')

  const incoming = Array.from(list)
  const accepted: File[] = []

  for (const candidate of incoming) {
    const problem = validate(candidate)
    if (problem) {
      setError(problem)
      continue
    }
    accepted.push(candidate)
  }

  if (!accepted.length) return

  let next = props.multiple
    ? [...files.value.map((entry) => entry.file), ...accepted]
    : accepted.slice(0, 1)

  if (props.maxFiles && next.length > props.maxFiles) {
    setError(`You can only add up to ${props.maxFiles} file${props.maxFiles === 1 ? '' : 's'}.`)
    next = next.slice(0, props.maxFiles)
  }

  files.value.forEach(revoke)
  files.value = next.map(makeEntry)
  commit()
}

function removeFile(id: string) {
  const entry = files.value.find((item) => item.id === id)
  if (entry) revoke(entry)
  files.value = files.value.filter((item) => item.id !== id)
  setError('')
  commit()
}

function handleZoneClick() {
  if (props.disabled) return
  inputRef.value?.click()
}

function onInputChange(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files?.length) addFiles(target.files)
  target.value = ''
}

function onDragEnter() {
  if (props.disabled) return
  dragDepth.value += 1
  isDragging.value = true
}

function onDragOver() {
  if (props.disabled) return
  isDragging.value = true
}

function onDragLeave() {
  if (props.disabled) return
  dragDepth.value = Math.max(0, dragDepth.value - 1)
  if (dragDepth.value === 0) isDragging.value = false
}

function onDrop(event: DragEvent) {
  if (props.disabled) return
  dragDepth.value = 0
  isDragging.value = false
  if (event.dataTransfer?.files?.length) addFiles(event.dataTransfer.files)
}
</script>

<style scoped>
.file-drop {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.dropzone {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  border: 1.5px dashed var(--border);
  border-radius: var(--radius);
  padding: 2rem 1.25rem;
  background: var(--muted);
  cursor: pointer;
  text-align: center;
  transition:
    border-color 0.15s ease,
    background-color 0.15s ease;
}

.dropzone:hover:not(.is-disabled) {
  border-color: color-mix(in srgb, var(--accent-strong) 55%, var(--border));
}

.dropzone:focus-visible {
  outline: 2px solid var(--accent-strong);
  outline-offset: 2px;
}

.dropzone.is-dragging {
  border-color: var(--accent-strong);
  background: color-mix(in srgb, var(--accent-strong) 8%, var(--muted));
}

.dropzone.is-disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.dropzone-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--accent-strong) 12%, transparent);
  color: var(--accent-strong);
}

.dropzone-title {
  margin: 0;
  color: var(--foreground);
  font-weight: 700;
}

.link-text {
  color: var(--accent-strong);
  text-decoration: underline;
  text-underline-offset: 2px;
}

.dropzone-hint {
  margin: 0;
  color: var(--muted-foreground);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
}

.file-drop-error {
  margin: 0;
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.file-row {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  border: 1px solid var(--border);
  border-radius: calc(var(--radius) - 4px);
  padding: 0.5rem 0.65rem;
  background: var(--background);
}

.file-thumb {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  flex: 0 0 auto;
  overflow: hidden;
  border-radius: 8px;
  background: var(--muted);
  color: var(--muted-foreground);
}

.file-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.file-meta {
  min-width: 0;
  flex: 1 1 auto;
}

.file-name {
  margin: 0;
  color: var(--foreground);
  font-weight: 600;
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  overflow-wrap: anywhere;
}

.file-size {
  margin: 0.1rem 0 0;
  color: var(--muted-foreground);
  font-size: 0.78rem;
}

.file-remove {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 999px;
  background: transparent;
  color: var(--muted-foreground);
  cursor: pointer;
}

.file-remove:hover {
  background: color-mix(in srgb, var(--destructive) 12%, transparent);
  color: var(--destructive);
}
</style>
