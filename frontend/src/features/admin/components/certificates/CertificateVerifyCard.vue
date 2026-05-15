<template>
  <ui-card class="panel">
    <template #header>
      <div class="panel-head">
        <h2 class="panel-title">Verify Certificate</h2>
        <span class="panel-note">By code or number</span>
      </div>
    </template>

    <form class="verify-form" @submit.prevent="$emit('submit')">
      <div class="input-wrap">
        <ui-input
          v-model="code"
          placeholder="Paste code or certificate number"
          required
          class="ui-input-full"
        />
      </div>
      <ui-button class="verify-btn" type="submit">Verify</ui-button>
    </form>

    <div v-if="result" class="result" :class="isValidResult ? 'result-valid' : 'result-invalid'">
      <div class="result-head">
        <p class="result-title">Verification result</p>
        <span class="status-badge" :class="isValidResult ? 'status-valid' : 'status-invalid'">{{
          isValidResult ? 'Valid' : 'Invalid'
        }}</span>
      </div>
      <template v-if="certificateData">
        <div class="result-grid">
          <p>
            <span class="label">Name</span><strong>{{ certificateData.full_name || '-' }}</strong>
          </p>
          <p>
            <span class="label">Team</span><strong>{{ certificateData.team_name || '-' }}</strong>
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
            <span class="label">Placement</span><strong>{{ certificateData.placement || '-' }}</strong>
          </p>
        </div>
      </template>
      <p v-if="result.message" class="result-message">{{ result.message }}</p>
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiButton from '@/components/ui/UiButton.vue'
import type { Certificate } from '@/api/.ts.schemas'

const props = defineProps<{ verifyCode: string; result: any }>()
const emit = defineEmits<{ (e: 'update:verifyCode', value: string): void; (e: 'submit'): void }>()
const code = computed({ get: () => props.verifyCode, set: (v) => emit('update:verifyCode', v) })
const certificateData = computed<Certificate | null>(() => {
  if (!props.result) return null
  const candidate = (props.result as { data?: Certificate }).data
  return candidate ?? (props.result as Certificate)
})
const isValidResult = computed(() => {
  if (!props.result) return false
  if (typeof props.result.is_valid === 'boolean') return props.result.is_valid
  return !!certificateData.value
})
</script>

<style scoped>
.panel {
  background: var(--muted);
  color: var(--muted-foreground);
}
.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
}
.panel-title {
  margin: 0;
  font-size: 1rem;
}
.panel-note {
  font-size: 0.8rem;
  color: var(--color-gray-500);
}
.verify-form {
  display: flex;
  gap: 10px;
  width: 100%;
}
.input-wrap {
  flex: 1;
}
.ui-input-full {
  width: 100%;
}
.verify-btn {
  min-width: 140px;
}
.result {
  border-radius: 14px;
  padding: 14px;
  margin-top: 12px;
  border: 1px solid var(--line-soft);
  background: var(--background);
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
  color: var(--muted-foreground);
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
  background: var(--muted);
  border: 1px solid var(--line-soft);
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.label {
  font-size: 12px;
  color: var(--color-gray-500);
}
.result-message {
  margin: 10px 0 0;
  color: var(--muted-foreground);
}
.result-valid {
  border-color: #86efac;
}
.result-invalid {
  border-color: #fca5a5;
}
</style>
