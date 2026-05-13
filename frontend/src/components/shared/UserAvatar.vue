<template>
  <div class="user-avatar-wrap" :style="avatarStyle">
    <img
      v-if="avatar"
      :src="avatar"
      :alt="altText"
      class="user-avatar"
      :style="avatarImageStyle"
    />
    <div
      v-else
      class="user-avatar user-avatar-fallback"
      :style="avatarImageStyle"
      :aria-label="altText"
    >
      {{ initials }}
    </div>
    <img
      v-if="avatarFrameUrl"
      :src="avatarFrameUrl"
      alt="Avatar frame"
      class="user-avatar-frame"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { readImagePosition, toObjectPosition } from '@/lib/imagePosition'

const props = withDefaults(
  defineProps<{
    avatar?: string | null
    username: string
    fullName?: string
    avatarFrameUrl?: string | null
    size?: number
    positionKey?: string
  }>(),
  {
    avatar: null,
    avatarFrameUrl: null,
    fullName: '',
    size: 42,
  },
)

const sourceName = computed(() => props.fullName?.trim() || props.username?.trim() || '')
const initials = computed(() => {
  const parts = sourceName.value.split(/\s+/).filter(Boolean)
  if (!parts.length) return '?'
  if (parts.length === 1) return (parts[0] ?? '').slice(0, 2).toUpperCase()
  return `${parts[0]?.charAt(0) ?? ''}${parts[1]?.charAt(0) ?? ''}`.toUpperCase()
})

const altText = computed(() => `${props.username} avatar`)
const avatarStyle = computed(() => ({
  width: `${props.size}px`,
  height: `${props.size}px`,
}))
const avatarImageStyle = computed(() => ({
  width: `${props.size}px`,
  height: `${props.size}px`,
  objectPosition: toObjectPosition(readImagePosition(props.positionKey)),
}))
</script>

<style scoped>
.user-avatar-wrap {
  position: relative;
  display: inline-block;
  flex-shrink: 0;
}

.user-avatar {
  border-radius: 999px;
  object-fit: cover;
  border: 1px solid var(--line-soft);
  display: block;
}

.user-avatar-fallback {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: var(--color-gray-700);
  background: color-mix(in srgb, var(--brand-100) 40%, white);
}

.user-avatar-frame {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  object-fit: contain;
}
</style>
