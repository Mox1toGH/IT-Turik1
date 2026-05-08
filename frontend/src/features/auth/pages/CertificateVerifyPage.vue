<template>
  <main class="verify-page">
    <ui-card class="verify-card">
      <h1>Certificate Verification</h1>
      <p class="muted">Enter code from certificate or open this page from QR code.</p>

      <form class="verify-form" @submit.prevent="submit">
        <ui-input v-model="codeInput" placeholder="Paste verification code" required />
        <ui-button type="submit">Verify</ui-button>
      </form>

      <div v-if="isLoading" class="result muted">Checking...</div>

      <div v-else-if="result">
        <p><strong>Valid:</strong> {{ result.is_valid ? 'Yes' : 'No' }}</p>
        <template v-if="result.data">
          <p><strong>Name:</strong> {{ result.data.full_name }}</p>
          <p><strong>Tournament:</strong> {{ result.data.tournament_name }}</p>
          <p><strong>Certificate number:</strong> {{ result.data.certificate_number }}</p>
          <p><strong>Placement:</strong> {{ result.data.placement }}</p>
        </template>
        <p v-if="result.message" class="muted">{{ result.message }}</p>
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
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.verify-card {
  width: 100%;
  max-width: 680px;
}

.verify-form {
  display: flex;
  gap: 10px;
  margin: 16px 0;
}

.muted {
  opacity: 0.75;
}
</style>
