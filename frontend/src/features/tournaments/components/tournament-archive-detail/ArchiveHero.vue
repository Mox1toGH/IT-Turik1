<template>
  <ui-card class="hero-card">
    <div class="hero" :style="heroStyle">
      <div class="hero-overlay" />
      <div class="hero-content">
        <p class="hero-kicker">Tournament Archive</p>
        <h1 class="hero-title">{{ name }}</h1>
        <p class="hero-dates">{{ formatDateRange(startDate, endDate) }}</p>
        <div class="hero-actions">
          <ui-button asLink to="/tournaments/archive" size="sm" variant="secondary">Back</ui-button>
          <ui-button asLink :to="`/tournaments/${tournamentId}`" size="sm" variant="secondary"
            >Open tournament</ui-button
          >
        </div>
      </div>
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import { formatDateRange } from './lib/format'

const props = defineProps<{
  tournamentId: number
  name: string
  banner?: string | null
  startDate?: string | null
  endDate?: string | null
}>()

const heroStyle = computed(() => {
  if (props.banner) {
    return {
      backgroundImage: `linear-gradient(120deg, rgb(15 23 42 / 70%), rgb(30 41 59 / 30%)), url(${props.banner})`,
    }
  }
  return {
    backgroundImage:
      'linear-gradient(120deg, color-mix(in srgb, var(--primary) 45%, transparent), color-mix(in srgb, var(--muted) 85%, transparent))',
  }
})
</script>

<style scoped>
.hero-card {
  overflow: hidden;
  padding: 0;
  border: 1px solid color-mix(in srgb, var(--line-soft) 70%, transparent);
}

.hero {
  position: relative;
  border-radius: 12px;
  min-height: 300px;
  background-size: cover;
  background-position: center;
  padding: 1.4rem;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgb(2 6 23 / 8%), rgb(2 6 23 / 68%));
}

.hero-content {
  position: relative;
  z-index: 1;
  color: white;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  max-width: 820px;
  min-height: 100%;
}

.hero-kicker,
.hero-dates,
.hero-title {
  margin: 0;
}

.hero-kicker {
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 0.8rem;
  opacity: 0.85;
}

.hero-title {
  font-size: clamp(1.45rem, 2.8vw, 2.2rem);
  line-height: 1.2;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: auto;
  padding-top: 0.75rem;
}

@media (max-width: 720px) {
  .hero {
    min-height: 260px;
    padding: 1rem;
  }
}
</style>
