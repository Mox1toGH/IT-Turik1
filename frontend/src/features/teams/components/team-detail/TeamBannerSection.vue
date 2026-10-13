<template>
  <section
    v-if="team?.banner || (isCaptain && !loading)"
    class="team-banner-panel"
    :class="{ 'team-banner-panel--empty': !team?.banner }"
  >
    <div v-if="team?.banner" class="hero-banner" :style="heroBannerStyle" />
    <button
      v-if="isCaptain && !loading"
      class="banner-edit-overlay"
      type="button"
      @click="emit('open')"
    >
      <avatar-edit-icon />
      {{ team?.banner ? 'Edit banner' : 'Add banner' }}
    </button>
  </section>
</template>

<script setup lang="ts">
import AvatarEditIcon from '@/icons/AvatarEditIcon.vue'
import type { TeamResponse } from '@/api/backendAPINinja.schemas'

interface Props {
  team?: TeamResponse
  loading: boolean
  isCaptain: boolean
  heroBannerStyle: Record<string, string>
}

defineProps<Props>()

const emit = defineEmits<{
  (e: 'open'): void
}>()
</script>

<style scoped>
.team-banner-panel {
  position: relative;
  min-height: 220px;
  overflow: hidden;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--card);
}

.team-banner-panel--empty {
  display: flex;
  min-height: 150px;
  align-items: center;
  justify-content: center;
  background: var(--subtle);
}

.hero-banner {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  z-index: 0;
}

.banner-edit-overlay {
  position: absolute;
  right: 1rem;
  bottom: 1rem;
  z-index: 1;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  min-height: 40px;
  padding: 0.55rem 0.8rem;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: var(--card);
  color: var(--foreground);
  font-weight: 800;
  cursor: pointer;
}
</style>
