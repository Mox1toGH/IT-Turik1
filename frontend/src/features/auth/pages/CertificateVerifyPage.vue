<template>
  <main class="verify-page">
    <ui-card class="verify-card">
      <div class="title-row">
        <h1>Certificate Verification</h1>
        <ui-button variant="secondary" @click="goBack">Back</ui-button>
      </div>
      <p class="muted">Enter code from certificate or open this page from QR code.</p>

      <form class="verify-form" @submit.prevent="submit">
        <div class="input-wrap">
          <ui-input v-model="codeInput" placeholder="Paste verification code" required />
        </div>
        <ui-button class="verify-btn" type="submit">Verify</ui-button>
      </form>

      <div v-if="isLoading" class="result result-loading">Checking...</div>

      <div v-else-if="result" class="result" :class="result.is_valid ? 'result-valid' : 'result-invalid'">
        <div class="result-head">
          <p class="result-title">Verification result</p>
          <span class="status-badge" :class="result.is_valid ? 'status-valid' : 'status-invalid'">
            {{ result.is_valid ? 'Valid' : 'Invalid' }}
          </span>
        </div>

        <template v-if="result.data">
          <div class="result-grid">
            <p><span class="label">Name</span><strong>{{ result.data.full_name || '-' }}</strong></p>
            <p><span class="label">Team</span><strong>{{ result.data.team_name || '-' }}</strong></p>
            <p><span class="label">Tournament</span><strong>{{ result.data.tournament_name || '-' }}</strong></p>
            <p><span class="label">Certificate number</span><strong>{{ result.data.certificate_number || '-' }}</strong></p>
            <p><span class="label">Placement</span><strong>{{ result.data.placement || '-' }}</strong></p>
          </div>
        </template>

        <p v-if="result.message" class="result-message">{{ result.message }}</p>
      </div>
    </ui-card>
  </main>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { $api } from '@/api/services'
import type { VerifyCertificateResponse } from '@/api/services/certificates/types'
import UiCard from '@/components/ui/UiCard.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiButton from '@/components/ui/UiButton.vue'

const route = useRoute()
const router = useRouter()

const codeInput = ref(String(route.params.code ?? '').trim())
const result = ref<VerifyCertificateResponse | null>(null)
const isLoading = ref(false)

watch(
  () => route.params.code,
  async (value) => {
    codeInput.value = String(value ?? '').trim()
    await verify()
  },
  { immediate: true },
)

function submit() {
  const code = codeInput.value.trim()
  if (!code) {
    return
  }
  router.push(`/certificates/verify/${encodeURIComponent(code)}`)
}

function goBack() {
  if (window.history.length > 1) {
    router.back()
    return
  }
  router.push('/')
}

async function verify() {
  const code = String(route.params.code ?? '').trim()
  if (!code) {
    result.value = null
    return
  }

  isLoading.value = true
  try {
    result.value = await $api.certificates.verifyByCode(code)
  } catch {
    result.value = { is_valid: false, message: 'Verification failed.' }
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.verify-page {
  min-height: 100%;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 24px;
  padding-top: 96px;
  box-sizing: border-box;
}

.verify-card {
  width: 100%;
  max-width: 680px;
}

.title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.verify-form {
  display: flex;
  gap: 10px;
  margin: 16px 0;
  width: 100%;
}

.input-wrap {
  flex: 1;
}

.input-wrap :deep(input) {
  width: 100%;
  min-height: 48px;
  font-size: 16px;
}

.verify-btn {
  min-width: 140px;
  min-height: 48px;
}

.result {
  border-radius: 14px;
  padding: 14px;
  margin-top: 12px;
  border: 1px solid #dbe3ee;
  background: #f8fafc;
}

.result-loading {
  color: #475569;
  font-weight: 600;
}

.result-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.result-title {
  margin: 0;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #334155;
  font-weight: 700;
}

.status-badge {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.status-valid {
  background: #dcfce7;
  color: #166534;
}

.status-invalid {
  background: #fee2e2;
  color: #991b1b;
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.result-grid p {
  margin: 0;
  padding: 10px;
  border-radius: 10px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.label {
  font-size: 12px;
  color: #64748b;
}

.result-message {
  margin: 10px 0 0;
  color: #475569;
}

.result-valid {
  border-color: #86efac;
}

.result-invalid {
  border-color: #fca5a5;
}

.muted {
  opacity: 0.75;
}

@media (max-width: 760px) {
  .verify-form {
    flex-direction: column;
  }

  .title-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .verify-btn {
    width: 100%;
  }

  .result-grid {
    grid-template-columns: 1fr;
  }
}
</style>
