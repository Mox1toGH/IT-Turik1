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
    <ui-button size="lg" @click="goToSettings">Settings</ui-button>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
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
}>()

const router = useRouter()

function goToSettings() {
  router.push('/profile/notifications/settings')
}
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
