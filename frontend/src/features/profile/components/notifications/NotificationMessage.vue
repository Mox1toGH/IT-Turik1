<template>
  <ui-expandable-text v-if="expandable" :lines="lines">
    <p class="notification-message">
      <NotificationMessagePart v-for="(part, index) in parts" :key="index" :part="part" />
    </p>
  </ui-expandable-text>
  <p v-else class="notification-message" :class="{ 'notification-message--clamp': clamp }">
    <NotificationMessagePart v-for="(part, index) in parts" :key="index" :part="part" />
  </p>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import UiExpandableText from '@/components/ui/UiExpandableText'
import NotificationMessagePart from './NotificationMessagePart.vue'
import { parseNotificationMessage } from '../../composables/useNotifications'

interface Props {
  message: string
  expandable?: boolean
  clamp?: boolean
  lines?: number
}

const props = withDefaults(defineProps<Props>(), {
  expandable: false,
  clamp: false,
  lines: 2,
})

const parts = computed(() => parseNotificationMessage(props.message))
</script>

<style scoped>
.notification-message {
  margin: 0;
  overflow-wrap: anywhere;
}

.notification-message--clamp {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
