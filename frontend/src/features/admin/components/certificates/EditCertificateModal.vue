<template>
  <ui-modal v-model="open" maxWidth="600px">
    <template #title>
      <h3 class="panel-title">Edit Certificate</h3>
    </template>

    <form id="editCertForm" class="edit-cert-modal-form" @submit.prevent="submit">
      <div class="modal-form-grid">
        <div class="form-item">
          <label class="form-label">User</label>
          <ui-select v-model="form.user" :options="userOptions" placeholder="Select user" />
        </div>
        <div class="form-item">
          <label class="form-label">Tournament</label>
          <ui-select
            v-model="form.tournament"
            :options="tournamentOptions"
            placeholder="Select tournament"
          />
        </div>
        <div class="form-item">
          <label class="form-label">Team (optional)</label>
          <ui-select v-model="form.team" :options="teamOptions" placeholder="No team" />
        </div>
        <div class="form-item">
          <label class="form-label">Template (optional)</label>
          <ui-select
            v-model="form.template"
            :options="templateOptions"
            placeholder="Default template"
          />
        </div>
        <div class="form-item">
          <label class="form-label">Placement</label>
          <ui-input v-model="form.placement" required placeholder="1st" />
        </div>
        <div class="form-item">
          <label class="form-label">Certificate number</label>
          <ui-input v-model="form.certificate_number" placeholder="CERT-YYYY-MM-DD" />
        </div>
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
import { computed, reactive, watch } from 'vue'
import UiModal from '@/components/ui/UiModal.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiSelect from '@/components/ui/UiSelect.vue'
import { useNotification } from '@/composables/useNotification'
import { useUpdateCertificate } from '@/api/certificates/certificates'
import type { CertificateResponse } from '@/api/backendAPINinja.schemas'

const props = defineProps<{
  cert: CertificateResponse | null
  userOptions: Array<{ value: number; label: string }>
  tournamentOptions: Array<{ value: number; label: string }>
  teamOptions: Array<{ value: number; label: string }>
  templateOptions: Array<{ value: number; label: string }>
}>()

const emit = defineEmits<{
  (e: 'update:cert', value: CertificateResponse | null): void
  (e: 'updated'): void
}>()

const { showNotification } = useNotification()
const { mutateAsync: updateCert, isPending: isUpdating } = useUpdateCertificate()

const open = computed({
  get: () => props.cert !== null,
  set: (v) => {
    if (!v) emit('update:cert', null)
  },
})

const form = reactive({
  user: 0,
  tournament: 0,
  team: 0,
  template: 0,
  placement: '',
  certificate_number: '',
})

watch(
  () => props.cert,
  (cert) => {
    if (!cert) return
    form.user = cert.user || 0
    form.tournament = cert.tournament || 0
    form.team = cert.team || 0
    form.template = cert.template || 0
    form.placement = cert.placement
    form.certificate_number = cert.certificate_number || ''
  },
  { immediate: true },
)

async function submit() {
  if (!props.cert) return

  try {
    await updateCert({
      uniqueCode: props.cert.unique_code,
      data: {
        user: form.user,
        tournament: form.tournament,
        team: form.team || null,
        template: form.template || null,
        placement: form.placement,
        certificate_number: form.certificate_number.trim() || undefined,
      },
    })

    showNotification('Certificate updated successfully.', 'success')
    emit('update:cert', null)
    emit('updated')
  } catch {
    showNotification('Failed to update certificate.', 'error')
  }
}
</script>

<style scoped>
.panel-title {
  margin: 0;
  font-size: 1rem;
}
.edit-cert-modal-form {
  padding: 10px 0;
}
.modal-form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1.25rem 1rem;
}
.form-item {
  display: grid;
  gap: 0.4rem;
}
.form-label {
  font-size: 0.85rem;
  font-weight: 600;
}
@media (max-width: 900px) {
  .modal-form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
