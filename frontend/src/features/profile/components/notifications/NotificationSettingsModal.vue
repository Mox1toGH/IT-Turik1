<template>
  <ui-modal :modelValue="isOpen" @update:modelValue="$emit('update:isOpen', $event)">
    <template #title>
      <h3>Notification Settings</h3>
    </template>

    <div v-if="isLoading" class="loading-state">
      <p>Loading settings...</p>
    </div>
    <div v-else-if="error" class="error-state">
      <p>Error loading settings.</p>
    </div>
    <div v-else class="settings-content">
      <div class="global-setting">
        <label class="setting-row">
          <div class="setting-info">
            <span class="setting-title">Disable All Email Notifications</span>
            <span class="setting-desc"
              >You will not receive any emails from the system if checked.</span
            >
          </div>
          <ui-switch
            :modelValue="settings?.global_config.emails_disabled_globally"
            @update:modelValue="handleGlobalToggle"
            :disabled="isUpdatingGlobal"
          />
        </label>
      </div>

      <div class="events-settings">
        <h4>Event Preferences</h4>
        <div class="event-list">
          <div v-for="config in settings?.configs" :key="config.event_type" class="event-item">
            <div class="event-info">
              <span class="event-title">{{ getEventTitle(config.event_type) }}</span>
            </div>
            <div class="event-toggles">
              <label class="toggle-label">
                <span class="toggle-text">System</span>
                <ui-switch
                  :modelValue="config.is_system_enabled"
                  @update:modelValue="(val) => handleEventToggle(config.event_type, 'system', val)"
                  :disabled="isUpdatingEvent"
                />
              </label>
              <label class="toggle-label">
                <span class="toggle-text">Email</span>
                <ui-switch
                  :modelValue="config.is_email_enabled"
                  @update:modelValue="(val) => handleEventToggle(config.event_type, 'email', val)"
                  :disabled="isUpdatingEvent"
                />
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <ui-button size="sm" variant="secondary" @click="$emit('update:isOpen', false)">
        Close
      </ui-button>
    </template>
  </ui-modal>
</template>

<script setup lang="ts">
import UiModal from '@/components/ui/UiModal.vue'
import UiSwitch from '@/components/ui/UiSwitch.vue'
import UiButton from '@/components/ui/UiButton.vue'
import {
  useNotificationSettings,
  useUpdateEventConfig,
  useUpdateGlobalConfig,
} from '@/api/queries/notifications'
import { useNotification } from '@/composables/useNotification'

defineProps<{
  isOpen: boolean
}>()

const { data: settings, isLoading, error } = useNotificationSettings()
const { mutate: updateEvent, isPending: isUpdatingEvent } = useUpdateEventConfig()
const { mutate: updateGlobal, isPending: isUpdatingGlobal } = useUpdateGlobalConfig()

const { showNotification } = useNotification()

const getEventTitle = (key: string) => {
  const event = settings.value?.event_types.find((e) => e.key === key)
  return event ? event.title : key
}

const handleGlobalToggle = (val: boolean) => {
  updateGlobal(
    { emails_disabled_globally: val },
    {
      onSuccess: () => showNotification('Global email settings updated', 'success'),
      onError: () => showNotification('Failed to update settings', 'error'),
    },
  )
}

const handleEventToggle = (eventType: string, channel: 'system' | 'email', val: boolean) => {
  const payload = {
    event_type: eventType,
    ...(channel === 'system' ? { is_system_enabled: val } : {}),
    ...(channel === 'email' ? { is_email_enabled: val } : {}),
  }
  updateEvent(payload, {
    onSuccess: () =>
      showNotification(`Settings for ${getEventTitle(eventType)} updated`, 'success'),
    onError: () => showNotification('Failed to update event setting', 'error'),
  })
}
</script>

<style scoped>
.settings-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.setting-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--muted);
  border-radius: 8px;
}

.setting-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.setting-title {
  font-weight: 600;
  color: var(--foreground);
}

.setting-desc {
  font-size: 0.8rem;
  color: var(--muted-foreground);
}

.events-settings h4 {
  margin: 0 0 1rem 0;
  font-size: 1.1rem;
}

.event-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.event-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  border: 1px solid var(--border);
  border-radius: 8px;
}

.event-title {
  font-weight: 500;
}

.event-toggles {
  display: flex;
  gap: 1rem;
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.toggle-text {
  font-size: 0.85rem;
  color: var(--muted-foreground);
}

.loading-state,
.error-state {
  padding: 2rem;
  text-align: center;
  color: var(--muted-foreground);
}
</style>
