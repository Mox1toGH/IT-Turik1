<template>
  <div class="notifications-filters">
    <ui-button
      variant="secondary"
      size="lg"
      :disabled="!hasUnread || isMarkingAll"
      @click="emit('mark-all-read')"
    >
      Mark all read
    </ui-button>
    <ui-button
      variant="danger"
      size="lg"
      :disabled="!hasNotifications || isDeletingAll"
      @click="emit('delete-all')"
    >
      Delete all
    </ui-button>
    <ui-button size="lg" @click="emit('open-settings')">Settings</ui-button>
  </div>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton'

interface Props {
  hasUnread: boolean
  hasNotifications: boolean
  isMarkingAll: boolean
  isDeletingAll: boolean
}

defineProps<Props>()

const emit = defineEmits<{
  (e: 'mark-all-read'): void
  (e: 'delete-all'): void
  (e: 'open-settings'): void
}>()
</script>

<style scoped>
.notifications-filters {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  justify-content: flex-end;
  align-items: center;
}

@media (max-width: 760px) {
  .notifications-filters {
    justify-content: flex-start;
  }
}
</style>
