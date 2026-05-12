<template>
  <ui-modal v-model="open" maxWidth="600px">
    <template #title>
      <h3 class="panel-title">Edit Certificate</h3>
    </template>

    <form id="editCertForm" class="edit-cert-modal-form" @submit.prevent="$emit('submit')">
      <div class="modal-form-grid">
        <div class="form-item"><label class="form-label">User</label><ui-select v-model="localForm.user" :options="userOptions" placeholder="Select user" /></div>
        <div class="form-item"><label class="form-label">Tournament</label><ui-select v-model="localForm.tournament" :options="tournamentOptions" placeholder="Select tournament" /></div>
        <div class="form-item"><label class="form-label">Team (optional)</label><ui-select v-model="localForm.team" :options="teamOptions" placeholder="No team" /></div>
        <div class="form-item"><label class="form-label">Template (optional)</label><ui-select v-model="localForm.template" :options="templateOptions" placeholder="Default template" /></div>
        <div class="form-item"><label class="form-label">Placement</label><ui-input v-model="localForm.placement" required placeholder="1st" /></div>
        <div class="form-item"><label class="form-label">Certificate number</label><ui-input v-model="localForm.certificate_number" placeholder="CERT-YYYY-MM-DD" /></div>
      </div>
    </form>

    <template #footer>
      <ui-button variant="secondary" @click="open = false">Cancel</ui-button>
      <ui-button type="submit" form="editCertForm" :disabled="isUpdating">
        {{ isUpdating ? 'Saving...' : 'Save Changes' }}
      </ui-button>
    </template>
  </ui-modal>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import UiModal from '@/components/ui/UiModal.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiSelect from '@/components/ui/UiSelect.vue'

const props = defineProps<{
  modelValue: boolean
  form: { user: number; tournament: number; team: number; template: number; placement: string; certificate_number: string }
  userOptions: Array<{ value: number; label: string }>
  tournamentOptions: Array<{ value: number; label: string }>
  teamOptions: Array<{ value: number; label: string }>
  templateOptions: Array<{ value: number; label: string }>
  isUpdating: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'update:form', value: typeof props.form): void
  (e: 'submit'): void
}>()

const open = computed({ get: () => props.modelValue, set: (v) => emit('update:modelValue', v) })
const localForm = computed({ get: () => props.form, set: (v) => emit('update:form', v) })
</script>

<style scoped>
.panel-title { margin: 0; font-size: 1rem; }
.edit-cert-modal-form { padding: 10px 0; }
.modal-form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1.25rem 1rem; }
.form-item { display: grid; gap: 0.4rem; }
.form-label { font-size: 0.85rem; font-weight: 600; }
@media (max-width: 900px) { .modal-form-grid { grid-template-columns: 1fr; } }
</style>
