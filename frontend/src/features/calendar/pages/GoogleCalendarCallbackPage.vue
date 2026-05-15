<template>
  <section class="page-shell callback-page">
    <ui-card class="callback-card">
      <div v-if="isProcessing" class="callback-status">
        <div class="spinner"></div>
        <p>Connecting Google Calendar...</p>
      </div>
      <div v-else-if="isSuccess" class="callback-status callback-status--success">
        <selected-icon class="status-icon status-icon--success" />
        <p>Google Calendar connected successfully!</p>
        <p class="text-muted">Redirecting to calendar...</p>
      </div>
      <div v-else class="callback-status callback-status--error">
        <cross-icon class="status-icon status-icon--error" />
        <p>Failed to connect Google Calendar</p>
        <p class="text-muted">{{ errorMessage }}</p>
        <ui-button variant="default" @click="goToCalendar">Back to Calendar</ui-button>
      </div>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import UiCard from '@/components/ui/UiCard.vue'
import UiButton from '@/components/ui/UiButton.vue'
import SelectedIcon from '@/icons/SelectedIcon.vue'
import CrossIcon from '@/icons/CrossIcon.vue'
import { callbackGoogleCalendar } from '@/api/accounts/accounts'

const router = useRouter()
const route = useRoute()

const isProcessing = ref(true)
const isSuccess = ref(false)
const errorMessage = ref('')

function goToCalendar() {
  router.push('/calendar')
}

onMounted(async () => {
  const code = route.query.code as string | undefined

  if (!code) {
    isProcessing.value = false
    errorMessage.value = 'No authorization code received.'
    return
  }

  try {
    await callbackGoogleCalendar({ code })
    isSuccess.value = true
    isProcessing.value = false
    setTimeout(() => router.push('/calendar'), 1500)
  } catch (e) {
    isProcessing.value = false
    errorMessage.value = 'Failed to connect. Please try again.'
  }
})
</script>

<style scoped>
.callback-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}

.callback-card {
  max-width: 400px;
  width: 100%;
  padding: 2rem;
}

.callback-status {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  text-align: center;
}

.status-icon {
  width: 48px;
  height: 48px;
}

.status-icon--success {
  color: #22940d;
}

.status-icon--error {
  color: var(--destructive);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
