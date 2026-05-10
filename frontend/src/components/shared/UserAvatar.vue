<template>
  <img
    v-if="avatar"
    :src="avatar"
    :alt="altText"
    class="user-avatar"
    :style="avatarStyle"
  />
  <div
    v-else
    class="user-avatar user-avatar-fallback"
    :style="avatarStyle"
    :aria-label="altText"
  >
    {{ initials }}
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    avatar?: string | null
    username: string
    fullName?: string
    size?: number
  }>(),
  {
    avatar: null,
    fullName: '',
    size: 42,
  },
)

const sourceName = computed(() => props.fullName?.trim() || props.username?.trim() || '')
const initials = computed(() => {
  const parts = sourceName.value.split(/\s+/).filter(Boolean)
  if (!parts.length) return '?'
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase()
  return `${parts[0][0]}${parts[1][0]}`.toUpperCase()
})

const altText = computed(() => `${props.username} avatar`)
const avatarStyle = computed(() => ({
  width: `${props.size}px`,
  height: `${props.size}px`,
}))
</script>

<style scoped>
.user-avatar {
  border-radius: 999px;
  object-fit: cover;
  border: 1px solid var(--line-soft);
  flex-shrink: 0;
}

.user-avatar-fallback {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: var(--color-gray-700);
  background: color-mix(in srgb, var(--brand-100) 40%, white);
}
</style>
