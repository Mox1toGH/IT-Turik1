<template>
  <ui-card class="panel">
    <template #header>
      <div class="panel-head">
        <h2 class="panel-title">Create Certificate</h2>
        <span class="panel-note">Admin only action</span>
      </div>
    </template>

    <form class="form-grid" @submit.prevent="handleCreateCertificate">
      <label class="form-item">
        <p class="form-label">User</p>
        <ui-select-search
          v-model="form.fields.value.user"
          :options="userOptions"
          :is-invalid="!!form.errors.value.user"
          placeholder="Select user"
          @blur="form.validateField('user')"
        />
        <small v-if="form.errors.value.user" class="text-error">{{ form.errors.value.user }}</small>
      </label>

      <label class="form-item">
        <p class="form-label">Tournament</p>
        <ui-select-search
          v-model="form.fields.value.tournament"
          :options="tournamentOptions"
          :is-invalid="!!form.errors.value.tournament"
          placeholder="Select tournament"
          @blur="form.validateField('tournament')"
        />
        <small v-if="form.errors.value.tournament" class="text-error">{{
          form.errors.value.tournament
        }}</small>
      </label>

      <label class="form-item">
        <p class="form-label">Team (optional)</p>
        <ui-select-search
          v-model="form.fields.value.team"
          :options="teamOptions"
          :is-invalid="!!form.errors.value.team"
          placeholder="No team"
          @blur="form.validateField('team')"
        />
        <small v-if="form.errors.value.team" class="text-error">{{ form.errors.value.team }}</small>
      </label>

      <label class="form-item">
        <p class="form-label">Template (optional)</p>
        <ui-select-search
          v-model="form.fields.value.template"
          :options="templateOptions"
          :is-invalid="!!form.errors.value.template"
          placeholder="Default template"
          @blur="form.validateField('template')"
        />
        <small v-if="form.errors.value.template" class="text-error">{{
          form.errors.value.template
        }}</small>
      </label>

      <label class="form-item">
        <p class="form-label">Placement</p>
        <ui-input
          v-model="form.fields.value.placement"
          :is-invalid="!!form.errors.value.placement"
          placeholder="1st"
          required
          @blur="form.validateField('placement')"
        />
        <small v-if="form.errors.value.placement" class="text-error">{{
          form.errors.value.placement
        }}</small>
      </label>

      <label class="form-item">
        <p class="form-label">Certificate number (optional)</p>
        <ui-input
          v-model="form.fields.value.certificate_number"
          :is-invalid="!!form.errors.value.certificate_number"
          placeholder="Leave empty for auto: CERT-YYYY-MM-DD"
          @blur="form.validateField('certificate_number')"
        />
        <small v-if="form.errors.value.certificate_number" class="text-error">{{
          form.errors.value.certificate_number
        }}</small>
      </label>

      <ui-button type="submit" class="submit" :disabled="isCreating">
        {{ isCreating ? 'Creating...' : 'Create Certificate' }}
      </ui-button>
    </form>
  </ui-card>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiButton from '@/components/ui/UiButton.vue'
import { useForm } from '@/composables/useForm'
import { CreateCertificateSchema } from '@/schemas/certificates.schema'
import { useNotification } from '@/composables/useNotification'
import { useCreateCertificate } from '@/api/certificates/certificates'
import UiSelectSearch from '@/components/ui/UiSelectSearch.vue'

defineProps<{
  userOptions: Array<{ value: number; label: string }>
  tournamentOptions: Array<{ value: number; label: string }>
  teamOptions: Array<{ value: number; label: string }>
  templateOptions: Array<{ value: number; label: string }>
}>()

const { showNotification } = useNotification()

const form = useForm(CreateCertificateSchema, {
  user: 0,
  tournament: 0,
  team: 0,
  template: 0,
  placement: '',
  certificate_number: '',
})

const { mutateAsync: createCertificate, isPending: isCreating } = useCreateCertificate()

const handleCreateCertificate = async () => {
  if (!form.fields.value.user || !form.fields.value.tournament) {
    showNotification('Please select user and tournament.', 'error')
    return
  }

  try {
    await createCertificate({
      data: {
        user: form.fields.value.user,
        tournament: form.fields.value.tournament,
        team: form.fields.value.team || null,
        template: form.fields.value.template || null,
        placement: form.fields.value.placement,
        certificate_number: form.fields.value.certificate_number.trim(),
      },
    })

    showNotification('Certificate created successfully.', 'success')
    form.reset()
  } catch {
    showNotification('Failed to create certificate.', 'error')
  }
}
</script>

<style scoped>
.panel {
  background: var(--muted);
  color: var(--muted-foreground);
}
.panel-head {
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
}
.form-grid {
  align-items: end;
  gap: 0.75rem;
}
.form-grid :deep(.select-trigger) {
  background: var(--input) !important;
  border-color: var(--border) !important;
  color: var(--foreground) !important;
  border-radius: 12px !important;
  font-weight: 400 !important;
  padding: 0.75rem 0.85rem !important;
}
.form-grid :deep(.select-trigger:focus-visible) {
  box-shadow: 0 0 0 3px var(--ring) !important;
}
.form-item {
  display: grid;
  gap: 0.4rem;
}
.form-label {
  font-size: 0.85rem;
  font-weight: 600;
}
.submit {
  width: fit-content;
}
@media (max-width: 900px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
