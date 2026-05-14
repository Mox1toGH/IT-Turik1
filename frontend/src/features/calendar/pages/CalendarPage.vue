<template>
  <section class="page-shell calendar-page">
    <ui-card class="calendar-hero">
      <div>
        <p class="eyebrow">Schedule</p>
        <div class="title-row">
          <calendar-title-icon class="title-icon" />
          <h1>Calendar</h1>
        </div>
        <p class="sub">Events, consultations, deadlines and round milestones across your tournaments.</p>
      </div>
    </ui-card>

    <ui-card>
      <template #error>
        <div style="display: flex; height: 300px; justify-content: center; align-items: center">
          <p>Failed to load calendar data (code: {{ error?.code }})</p>
        </div>
      </template>

      <ui-skeleton-loader :loading="isLoading">
        <template #skeleton>
          <div class="calendar-skeleton">
            <div class="skeleton-nav">
              <ui-skeleton variant="rect" width="32px" height="32px" />
              <ui-skeleton variant="rect" width="180px" height="24px" />
              <ui-skeleton variant="rect" width="32px" height="32px" />
            </div>
            <div class="skeleton-grid">
              <ui-skeleton v-for="i in 42" :key="i" variant="rect" height="90px" />
            </div>
          </div>
        </template>

        <div v-if="isError" class="calendar-error">
          <p>Error while fetching calendar data</p>
        </div>

        <div v-else-if="!hasItems" class="calendar-empty">
          <calendar-icon class="empty-icon" />
          <p>No upcoming events or deadlines</p>
          <p class="text-muted">Join a tournament to see its schedule here</p>
        </div>

        <schedule-calendar
          v-else
          :events="events"
          :rounds="rounds"
        />
      </ui-skeleton-loader>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import CalendarIcon from '@/icons/CalendarIcon.vue'
import CalendarTitleIcon from '@/icons/CalendarTitleIcon.vue'
import ScheduleCalendar from '../components/ScheduleCalendar.vue'
import { useMyCalendar } from '@/api/queries/tournaments'
import { parseApiError } from '@/api/errors'
import { computed } from 'vue'

const { data, isLoading, isError, error: calendarError } = useMyCalendar()
const error = computed(() => parseApiError(calendarError.value))

const events = computed(() => data.value?.events ?? [])
const rounds = computed(() => data.value?.rounds ?? [])
const hasItems = computed(() => events.value.length > 0 || rounds.value.length > 0)
</script>

<style scoped>
.calendar-page {
  display: grid;
  gap: 1rem;
}

.calendar-hero {
  padding: 1.4rem;
  background:
    linear-gradient(130deg, rgba(15, 118, 110, 0.95), rgba(20, 184, 166, 0.88)),
    linear-gradient(45deg, rgba(249, 115, 22, 0.2), transparent);
  color: white;
  border: none;
}

.eyebrow {
  margin: 0;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 0.75rem;
  opacity: 0.85;
}

h1 {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(1.4rem, 1.3vw + 1rem, 2rem);
}

.title-row {
  margin-top: 0.45rem;
  display: flex;
  align-items: center;
  gap: 0.55rem;
}

.title-icon {
  width: 1.3rem;
  height: 1.3rem;
  opacity: 0.92;
}

.sub {
  margin: 0.5rem 0 0;
  opacity: 0.92;
}

.calendar-skeleton {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.skeleton-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 1px;
}

.calendar-error,
.calendar-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  gap: 0.5rem;
  text-align: center;
}

.empty-icon {
  width: 48px;
  height: 48px;
  color: var(--muted-foreground);
  opacity: 0.5;
}
</style>
