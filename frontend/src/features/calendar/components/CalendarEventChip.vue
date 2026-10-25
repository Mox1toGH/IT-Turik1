<template>
  <span
    :class="['chip', `chip--${chip.color}`, 'chip--clickable']"
    :title="chip.title"
    @click.stop="$emit('navigate', chip)"
  >
    {{ label }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { truncateText } from '@/lib/utils'
import type { CalendarItem } from '../composables/useCalendarGrid'

interface Props {
  chip: CalendarItem
  maxLength?: number
}

const props = withDefaults(defineProps<Props>(), { maxLength: 12 })

defineEmits<{
  navigate: [item: CalendarItem]
}>()

const label = computed(() => truncateText(props.chip.title, props.maxLength))
</script>

<style scoped>
.chip {
  font-size: 0.65rem;
  font-weight: 600;
  padding: 1px 4px;
  border-radius: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.4;
}

.chip--clickable {
  cursor: pointer;
}

.chip--clickable:hover {
  filter: brightness(0.9);
}

.chip--primary {
  background: color-mix(in srgb, var(--primary) 15%, transparent);
  color: var(--primary);
}

.chip--green {
  background: var(--success-soft);
  color: var(--success);
}

.chip--orange {
  background: color-mix(in srgb, var(--warning) 15%, transparent);
  color: var(--warning);
}

.chip--red {
  background: color-mix(in srgb, var(--destructive) 12%, transparent);
  color: var(--destructive);
}

@media (max-width: 768px) {
  .chip {
    font-size: 0.55rem;
  }
}
</style>
