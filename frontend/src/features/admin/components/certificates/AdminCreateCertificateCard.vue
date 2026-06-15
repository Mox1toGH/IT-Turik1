<template>
  <ui-card class="panel">
    <template #header>
      <div class="panel-head">
        <h2 class="panel-title">Create Certificate</h2>
        <span class="panel-note">Admin only action</span>
      </div>
    </template>

    <form class="form-grid" @submit.prevent="$emit('submit')">
      <div class="form-item">
        <label class="form-label">User</label>
        <ui-select v-model="localForm.user" :options="userOptions" placeholder="Select user" />
      </div>

      <div class="form-item">
        <label class="form-label">Tournament</label>
        <ui-select v-model="localForm.tournament" :options="tournamentOptions" placeholder="Select tournament" />
      </div>

      <div class="form-item">
        <label class="form-label">Team (optional)</label>
        <ui-select v-model="localForm.team" :options="teamOptions" placeholder="No team" />
      </div>

      <div class="form-item">
        <label class="form-label">Template (optional)</label>
        <ui-select v-model="localForm.template" :options="templateOptions" placeholder="Default template" />
      </div>

      <div class="form-item">
        <label class="form-label">Placement</label>
        <ui-input v-model="localForm.placement" required placeholder="1st" />
      </div>

      <div class="form-item">
        <label class="form-label">Certificate number (optional)</label>
        <ui-input v-model="localForm.certificate_number" placeholder="Leave empty for auto: CERT-YYYY-MM-DD" />
      </div>

      <ui-button type="submit" class="submit" :disabled="isCreating">
        {{ isCreating ? 'Creating...' : 'Create Certificate' }}
      </ui-button>
    </form>
  </ui-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiSelect from '@/components/ui/UiSelect.vue'

const props = defineProps<{
  form: {
    user: number
    tournament: number
    team: number
    template: number
    placement: string
    certificate_number: string
  }
  userOptions: Array<{ value: number; label: string }>
  tournamentOptions: Array<{ value: number; label: string }>
  teamOptions: Array<{ value: number; label: string }>
  templateOptions: Array<{ value: number; label: string }>
  isCreating: boolean
}>()

const emit = defineEmits<{
  (e: 'update:form', value: typeof props.form): void
  (e: 'submit'): void
}>()

const localForm = computed({
  get: () => props.form,
  set: (value) => emit('update:form', value),
})
</script>

<style scoped>
.panel { background: var(--muted); color: var(--muted-foreground); }
.panel-head { display: flex; justify-content: space-between; align-items: center; gap: 0.75rem; }
.panel-title { margin: 0; font-size: 1rem; }
.panel-note { font-size: 0.8rem; color: var(--color-gray-500); }
.form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0.75rem; align-items: end; }
.form-grid :deep(.select-trigger) { background: var(--input) !important; border-color: var(--border) !important; color: var(--foreground) !important; border-radius: 12px !important; font-weight: 400 !important; padding: 0.75rem 0.85rem !important; }
.form-grid :deep(.select-trigger:focus-visible) { box-shadow: 0 0 0 3px var(--ring) !important; }
.form-item { display: grid; gap: 0.4rem; }
.form-label { font-size: 0.85rem; font-weight: 600; }
.submit { width: fit-content; }
@media (max-width: 900px) { .form-grid { grid-template-columns: 1fr; } }
</style>
