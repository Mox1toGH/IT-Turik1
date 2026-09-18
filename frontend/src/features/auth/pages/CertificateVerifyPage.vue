<!-- TODO: maybe add this page to another folder.
 cuz it's not auth feature -->

<template>
  <main class="verify-page">
    <section class="verify-shell page-shell">
      <header class="verify-hero">
        <div class="verify-hero-copy">
          <div class="breadcrumb-label">
            <span>Certificates</span>
            <span aria-hidden="true">/</span>
            <span>Verify</span>
          </div>

          <h1 class="text-6xl">Certificate Verification</h1>
          <p class="section-subtitle text-xl">
            Enter the code from a certificate, or open this page from its QR code.
          </p>
        </div>

        <div class="hero-actions">
          <ui-button variant="secondary" size="lg" @click="goBack">Back</ui-button>
        </div>
      </header>

      <div class="verify-rule" aria-hidden="true"></div>

      <ui-card class="verify-card">
        <form class="verify-form" @submit.prevent="submit">
          <div class="input-wrap">
            <ui-input v-model="codeInput" placeholder="Paste verification code" required />
          </div>
          <ui-button class="verify-btn" type="submit" size="lg">Verify</ui-button>
        </form>

        <div v-if="isLoading" class="result result-loading">Checking...</div>

        <div
          v-else-if="result"
          class="result"
          :class="isValidResult ? 'result-valid' : 'result-invalid'"
        >
          <div class="result-head">
            <p class="result-title">Verification result</p>
            <ui-badge :variant="isValidResult ? 'green' : 'red'">
              {{ isValidResult ? 'Valid' : 'Invalid' }}
            </ui-badge>
          </div>

          <template v-if="certificateData">
            <div class="result-grid">
              <p>
                <span class="label">Name</span
                ><strong>{{ certificateData.full_name || '-' }}</strong>
              </p>
              <p>
                <span class="label">Team</span
                ><strong>{{ certificateData.team_name || '-' }}</strong>
              </p>
              <p>
                <span class="label">Tournament</span
                ><strong>{{ certificateData.tournament_name || '-' }}</strong>
              </p>
              <p>
                <span class="label">Certificate number</span
                ><strong>{{ certificateData.certificate_number || '-' }}</strong>
              </p>
              <p>
                <span class="label">Placement</span
                ><strong>{{ certificateData.placement || '-' }}</strong>
              </p>
            </div>
          </template>

          <p v-if="result.message" class="result-message">{{ result.message }}</p>
        </div>
      </ui-card>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import UiInput from '@/components/ui/UiInput.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import {
  verifyCertificate,
  type VerifyCertificateQueryResult,
} from '@/api/certificates/certificates'
import type { Certificate } from '@/api/.ts.schemas'

type Result = VerifyCertificateQueryResult & { is_valid?: boolean; message?: string }

const route = useRoute()
const router = useRouter()

const codeInput = ref(String(route.params.code ?? '').trim())

const result = ref<Result | null>(null)
const isValidResult = computed(() => {
  if (!result.value) return false
  if (typeof result.value.is_valid === 'boolean') return result.value.is_valid
  return !!certificateData.value
})

const isLoading = ref(false)
const certificateData = computed<Certificate | null>(() => {
  if (!result.value) return null
  const candidate = (result.value as { data?: Certificate }).data
  return candidate ?? (result.value as unknown as Certificate)
})

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
    result.value = await verifyCertificate(code)
  } catch {
    result.value = { is_valid: false, message: 'Verification failed.' } as Result
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

.verify-shell {
  width: 100%;
  max-width: 760px;
  gap: 1.4rem;
}

.verify-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1.5rem;
}

.verify-hero-copy {
  min-width: 0;
}

.breadcrumb-label {
  display: inline-flex;
  align-items: center;
  gap: 0.7rem;
  margin-bottom: 0.75rem;
  color: var(--accent-strong);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.verify-hero h1 {
  margin: 0;
  max-width: 760px;
  color: var(--foreground);
  font-size: var(--text-4xl);
  line-height: var(--text-4xl--line-height);
  font-family: var(--font-display);
  font-weight: 800;
}

.verify-hero .section-subtitle {
  margin: 0.45rem 0 0;
  max-width: 620px;
  font-size: var(--text-base);
  line-height: var(--text-base--line-height);
  color: var(--muted-foreground);
}

.hero-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: flex-end;
  align-items: center;
}

.verify-rule {
  height: 1px;
  margin: 0.7rem 0 0.9rem;
  background: var(--line-soft);
}

.verify-card {
  padding: 1.4rem;
}

.verify-form {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
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
  border: 1px solid var(--border);
  background: color-mix(in srgb, var(--muted) 60%, transparent);
}

.result-loading {
  color: var(--muted-foreground);
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
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted-foreground);
  font-weight: 700;
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
  background: var(--background);
  border: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.label {
  font-size: 12px;
  color: var(--muted-foreground);
}

.result-message {
  margin: 10px 0 0;
  color: var(--muted-foreground);
}

.result-valid {
  border-color: color-mix(in srgb, var(--success, #22c55e) 45%, var(--border));
}

.result-invalid {
  border-color: color-mix(in srgb, var(--danger, #ef4444) 45%, var(--border));
}

@media (max-width: 760px) {
  .verify-page {
    padding: 16px;
    padding-top: 64px;
  }

  .verify-hero {
    align-items: stretch;
    flex-direction: column;
    gap: 1rem;
  }

  .verify-hero h1 {
    font-size: var(--text-3xl);
    line-height: var(--text-3xl--line-height);
  }

  .verify-hero .section-subtitle {
    font-size: var(--text-sm);
    line-height: var(--text-sm--line-height);
  }

  .hero-actions {
    justify-content: flex-start;
  }

  .verify-form {
    flex-direction: column;
  }

  .verify-btn {
    width: 100%;
  }

  .result-grid {
    grid-template-columns: 1fr;
  }
}
</style>
