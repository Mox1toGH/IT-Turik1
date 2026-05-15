<template>
  <section class="page-shell calendar-page">
    <ui-card class="calendar-hero">
      <div>
        <p class="eyebrow">Schedule</p>
        <div class="title-row">
          <calendar-title-icon class="title-icon" />
          <h1>Calendar</h1>
        </div>
        <p class="sub">
          Events, consultations, deadlines and round milestones across your tournaments.
        </p>
      </div>
      <div class="gcal-actions">
        <template v-if="gcalLoading">
          <ui-button size="sm" variant="secondary" disabled>
            <loading-icon class="gcal-icon spin" />
            Loading…
          </ui-button>
        </template>
        <template v-else-if="gcalConnected">
          <ui-button size="sm" variant="ghost" @click="exportAll" :disabled="isExporting || !hasItems">
            <google-calendar-icon class="gcal-icon" />
            {{ isExporting ? 'Exporting…' : 'Export All to Google' }}
          </ui-button>
          <ui-button size="sm" variant="danger" @click="disconnectGcal">
            Disconnect
          </ui-button>
        </template>
        <template v-else>
          <ui-button size="sm" variant="secondary" @click="connectGcal">
            <google-calendar-icon class="gcal-icon" />
            Connect Google Calendar
          </ui-button>
        </template>
      </div>
    </ui-card>

    <ui-card>
      <template #error>
        <div style="display: flex; height: 300px; justify-content: center; align-items: center">
          <p>Failed to load calendar data (code: {{ calendarError?.code }})</p>
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
          :gcal-connected="gcalConnected"
          @export-event="exportEvent"
          @export-round="exportRound"
        />
      </ui-skeleton-loader>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import CalendarIcon from '@/icons/CalendarIcon.vue'
import CalendarTitleIcon from '@/icons/CalendarTitleIcon.vue'
import GoogleCalendarIcon from '@/icons/GoogleCalendarIcon.vue'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import ScheduleCalendar from '../components/ScheduleCalendar.vue'
import { computed, onMounted, ref } from 'vue'
import { googleCalendarService } from '@/api/services/google-calendar'
import { useGetMyCalendar } from '@/api/tournaments/tournaments'

const { data, isLoading, isError, error: calendarError } = useGetMyCalendar()

const events = computed(() => data.value?.events ?? [])
const rounds = computed(() => data.value?.rounds ?? [])
const hasItems = computed(() => events.value.length > 0 || rounds.value.length > 0)

const gcalConnected = ref(false)
const gcalLoading = ref(true)
const isExporting = ref(false)

onMounted(async () => {
  try {
    const status = await googleCalendarService.getStatus()
    gcalConnected.value = status.connected
  } catch {
    gcalConnected.value = false
  } finally {
    gcalLoading.value = false
  }
})

async function connectGcal() {
  try {
    const { auth_url } = await googleCalendarService.connect()
    window.location.href = auth_url
  } catch (e) {
    console.error('Failed to get Google Calendar auth URL', e)
  }
}

async function disconnectGcal() {
  try {
    await googleCalendarService.disconnect()
    gcalConnected.value = false
  } catch (e) {
    console.error('Failed to disconnect Google Calendar', e)
  }
}

async function exportAll() {
  if (isExporting.value) return
  isExporting.value = true
  try {
    const eventIds = events.value.map((e: any) => e.id)
    const roundIds = rounds.value.map((r: any) => r.id)
    await googleCalendarService.exportToGoogle({
      event_ids: eventIds,
      round_ids: roundIds,
    })
  } catch (e) {
    console.error('Export failed', e)
  } finally {
    isExporting.value = false
  }
}

async function exportEvent(eventId: number) {
  try {
    await googleCalendarService.exportToGoogle({ event_ids: [eventId] })
  } catch (e) {
    console.error('Export event failed', e)
  }
}

async function exportRound(roundId: number) {
  try {
    await googleCalendarService.exportToGoogle({ round_ids: [roundId] })
  } catch (e) {
    console.error('Export round failed', e)
  }
}
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
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  flex-wrap: wrap;
}

.gcal-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex-wrap: wrap;
}

.gcal-icon {
  width: 16px;
  height: 16px;
}

.spin {
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
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
