<template>
  <div class="day-detail">
    <div class="day-detail-header">
      <h4>{{ formattedDate(date) }}</h4>
      <ui-button size="sm" variant="ghost" @click="$emit('close')">
        <cross-icon />
      </ui-button>
    </div>

    <div v-if="items.length === 0" class="day-detail-empty">
      <p class="text-muted">No events for this day</p>
    </div>

    <div v-else class="day-detail-list">
      <div
        v-for="item in items"
        :key="item.id"
        :class="['day-detail-item', `day-detail-item--${item.color}`, 'day-detail-item--clickable']"
        @click="$emit('navigate', item)"
      >
        <div class="day-detail-item-header">
          <ui-badge :variant="item.color">{{ typeLabel(item.type) }}</ui-badge>
          <span v-if="item.link" class="day-detail-link">
            <a :href="item.link" target="_blank" rel="noopener noreferrer">
              <external-link-icon class="link-icon" />
              Join
            </a>
          </span>
          <span v-if="gcalConnected" class="day-detail-link">
            <a href="#" @click.stop.prevent="$emit('exportItem', item)">
              <google-calendar-icon class="link-icon" />
              GCal
            </a>
          </span>
        </div>
        <p class="day-detail-title">{{ item.title }}</p>
        <p v-if="item.description" class="day-detail-description">{{ item.description }}</p>
        <p class="day-detail-time text-muted">
          <clock-icon class="time-icon" />
          {{ formatTime(item.date) }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import UiBadge from '@/components/ui/UiBadge.vue'
import UiButton from '@/components/ui/UiButton.vue'
import CrossIcon from '@/icons/CrossIcon.vue'
import ClockIcon from '@/icons/ClockIcon.vue'
import ExternalLinkIcon from '@/icons/ExternalLinkIcon.vue'
import GoogleCalendarIcon from '@/icons/GoogleCalendarIcon.vue'
import { formatDate } from '@/lib/date'

interface CalendarItem {
  id: string
  title: string
  description: string
  date: Date
  type: 'meet' | 'event' | 'round-start' | 'round-deadline'
  color: 'primary' | 'green' | 'orange' | 'red'
  link?: string
  tournamentId?: number
}

interface Props {
  date: Date
  items: CalendarItem[]
  gcalConnected?: boolean
}

defineProps<Props>()
defineEmits<{ close: []; navigate: [item: CalendarItem]; exportItem: [item: CalendarItem] }>()

function typeLabel(type: CalendarItem['type']): string {
  switch (type) {
    case 'meet': return 'Consultation'
    case 'event': return 'Event'
    case 'round-start': return 'Round start'
    case 'round-deadline': return 'Deadline'
  }
}

function formattedDate(date: Date): string {
  return formatDate(date, { showHours: false })
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' })
}
</script>

<style scoped>
.day-detail {
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1rem;
  background: var(--card);
}

.day-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border);
}

.day-detail-header h4 {
  margin: 0;
  font-family: var(--font-display);
}

.day-detail-empty {
  text-align: center;
  padding: 1rem 0;
}

.day-detail-list {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.day-detail-item {
  padding: 0.6rem;
  border-radius: var(--radius);
  border-left: 3px solid;
}

.day-detail-item--clickable {
  cursor: pointer;
}

.day-detail-item--clickable:hover {
  filter: brightness(0.97);
}

.day-detail-item--primary {
  border-left-color: var(--primary);
  background: color-mix(in srgb, var(--primary) 5%, transparent);
}

.day-detail-item--green {
  border-left-color: #22940d;
  background: rgba(34, 148, 13, 0.05);
}

.day-detail-item--orange {
  border-left-color: var(--warning);
  background: color-mix(in srgb, var(--warning) 5%, transparent);
}

.day-detail-item--red {
  border-left-color: var(--destructive);
  background: color-mix(in srgb, var(--destructive) 5%, transparent);
}

.day-detail-item-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.3rem;
}

.day-detail-link a {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--primary);
  text-decoration: none;
}

.day-detail-link a:hover {
  text-decoration: underline;
}

.link-icon {
  width: 14px;
  height: 14px;
}

.day-detail-title {
  font-weight: 600;
  margin: 0 0 0.15rem;
}

.day-detail-description {
  font-size: 0.85rem;
  color: var(--muted-foreground);
  margin: 0 0 0.3rem;
}

.day-detail-time {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.8rem;
  margin: 0;
}

.time-icon {
  width: 14px;
  height: 14px;
}
</style>
