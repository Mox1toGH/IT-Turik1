<template>
  <section class="page-shell">
    <ui-card>
      <template #header>
        <div class="head">
          <div>
            <p class="section-eyebrow">Admin</p>
            <h1 class="section-title">Certificates</h1>
            <p class="section-subtitle">
              Create certificates for users, manage template library, and verify certificate codes.
            </p>
          </div>
          <router-link to="/admin/role-codes" class="back-link">Back to Activation Codes</router-link>
        </div>
      </template>

      <div class="layout">
        <ui-card class="panel">
          <template #header>
            <div class="panel-head">
              <h2 class="panel-title">Create Certificate</h2>
              <span class="panel-note">Admin only action</span>
            </div>
          </template>

          <form class="form-grid" @submit.prevent="handleCreateCertificate">
            <div class="form-item">
              <label class="form-label">User</label>
              <ui-select v-model="createForm.user" :options="userOptions" placeholder="Select user" />
            </div>

            <div class="form-item">
              <label class="form-label">Tournament</label>
              <ui-select
                v-model="createForm.tournament"
                :options="tournamentOptions"
                placeholder="Select tournament"
              />
            </div>

            <div class="form-item">
              <label class="form-label">Team (optional)</label>
              <ui-select v-model="createForm.team" :options="teamOptions" placeholder="No team" />
            </div>

            <div class="form-item">
              <label class="form-label">Template (optional)</label>
              <ui-select
                v-model="createForm.template"
                :options="templateOptions"
                placeholder="Default template"
              />
            </div>

            <div class="form-item">
              <label class="form-label">Placement</label>
              <ui-input v-model="createForm.placement" required placeholder="1st place" />
            </div>

            <div class="form-item">
              <label class="form-label">Certificate number</label>
              <ui-input v-model="createForm.certificate_number" required placeholder="CERT-2026-001" />
            </div>

            <ui-button type="submit" class="submit" :disabled="isCreating">
              {{ isCreating ? 'Creating...' : 'Create Certificate' }}
            </ui-button>
          </form>
        </ui-card>

        <ui-card class="panel">
          <template #header>
            <div class="panel-head">
              <h2 class="panel-title">Template Library</h2>
              <span class="panel-note">Upload and preview</span>
            </div>
          </template>

          <form class="template-form" @submit.prevent="handleUploadTemplate">
            <div class="form-item">
              <label class="form-label">Template name</label>
              <ui-input v-model="templateForm.name" required placeholder="Summer Cup 2026" />
            </div>

            <div class="form-item">
              <label class="form-label">Image</label>
              <input class="file-input" type="file" accept="image/*" @change="onTemplateFileChange" required />
            </div>

            <label class="check">
              <input v-model="templateForm.is_default" type="checkbox" />
              Make default template
            </label>

            <ui-button type="submit" :disabled="isUploading" class="submit">
              {{ isUploading ? 'Uploading...' : 'Upload Template' }}
            </ui-button>
          </form>

          <ui-skeleton-loader :loading="isTemplatesLoading">
            <template #skeleton>
              <div class="templates-grid">
                <ui-skeleton v-for="i in 3" :key="i" variant="rect" width="100%" />
              </div>
            </template>

            <p v-if="isTemplatesError" class="text-muted">Failed to load templates.</p>
            <p v-else-if="!templates?.length" class="text-muted">No templates uploaded yet.</p>

            <div v-else class="templates-grid">
              <ui-card v-for="tpl in templates" :key="tpl.id" class="template-card">
                <template #header>
                  <div class="template-head">
                    <strong>{{ tpl.name }}</strong>
                    <ui-badge :variant="tpl.is_default ? 'green' : 'gray'">
                      {{ tpl.is_default ? 'Default' : 'Template' }}
                    </ui-badge>
                  </div>
                </template>

                <img v-if="tpl.image_url" :src="tpl.image_url" :alt="tpl.name" class="preview" />
              </ui-card>
            </div>
          </ui-skeleton-loader>
        </ui-card>

        <ui-card class="panel">
          <template #header>
            <div class="panel-head">
              <h2 class="panel-title">Verify Certificate</h2>
              <span class="panel-note">By code or number</span>
            </div>
          </template>

          <form class="verify-form" @submit.prevent="handleVerify">
            <div class="form-item">
              <label class="form-label">Code or certificate number</label>
              <ui-input v-model="verifyCode" required placeholder="Paste code" />
            </div>
            <ui-button type="submit" class="submit">Verify</ui-button>
          </form>

          <ui-card v-if="verifyResult" class="verify-result">
            <p><strong>Valid:</strong> {{ verifyResult.is_valid ? 'Yes' : 'No' }}</p>
            <p v-if="verifyResult.data"><strong>User:</strong> {{ verifyResult.data.full_name }}</p>
            <p v-if="verifyResult.data"><strong>Tournament:</strong> {{ verifyResult.data.tournament_name }}</p>
            <p v-if="verifyResult.message" class="text-muted">{{ verifyResult.message }}</p>
          </ui-card>
        </ui-card>
      </div>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiSelect from '@/components/ui/UiSelect.vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import { useUsers } from '@/api/queries/accounts'
import { useTeams } from '@/api/queries/teams'
import { useTournaments } from '@/api/queries/tournaments'
import {
  useCertificateTemplates,
  useCreateCertificate,
  useUploadCertificateTemplate,
} from '@/api/queries/certificates'
import { $api } from '@/api/services'
import { useNotification } from '@/composables/useNotification'

const { showNotification } = useNotification()

const { data: users } = useUsers()
const { data: teams } = useTeams()
const { data: tournamentsResponse } = useTournaments({
  page: 1,
  pageSize: 200,
  searchQuery: '',
  status: undefined as any,
})

const {
  data: templates,
  isLoading: isTemplatesLoading,
  isLoadingError: isTemplatesError,
} = useCertificateTemplates()
const { mutateAsync: createCertificate, isPending: isCreating } = useCreateCertificate()
const { mutateAsync: uploadTemplate, isPending: isUploading } = useUploadCertificateTemplate()

const createForm = ref({
  user: 0,
  tournament: 0,
  team: 0,
  template: 0,
  placement: '',
  certificate_number: '',
})

const templateForm = ref({
  name: '',
  file: null as File | null,
  is_default: false,
})

const verifyCode = ref('')
const verifyResult = ref<any>(null)

const userOptions = computed(() =>
  (users.value || []).map((u) => ({
    value: u.id,
    label: `${u.full_name || u.username} (#${u.id})`,
  })),
)

const tournamentOptions = computed(() =>
  (tournamentsResponse.value?.data || []).map((t) => ({
    value: t.id,
    label: `${t.name} (#${t.id})`,
  })),
)

const teamOptions = computed(() => [
  { value: 0, label: 'No team' },
  ...(teams.value || []).map((t) => ({ value: t.id, label: `${t.name} (#${t.id})` })),
])

const templateOptions = computed(() => [
  { value: 0, label: 'Default template' },
  ...(templates.value || []).map((t) => ({
    value: t.id,
    label: t.is_default ? `${t.name} (default)` : t.name,
  })),
])

const onTemplateFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  templateForm.value.file = target.files?.[0] || null
}

const handleCreateCertificate = async () => {
  if (!createForm.value.user || !createForm.value.tournament) {
    showNotification('Please select user and tournament.', 'error')
    return
  }

  try {
    await createCertificate({
      user: createForm.value.user,
      tournament: createForm.value.tournament,
      team: createForm.value.team || null,
      template: createForm.value.template || null,
      placement: createForm.value.placement,
      certificate_number: createForm.value.certificate_number,
    })

    showNotification('Certificate created successfully.', 'success')
    createForm.value.placement = ''
    createForm.value.certificate_number = ''
  } catch {
    showNotification('Failed to create certificate.', 'error')
  }
}

const handleUploadTemplate = async () => {
  if (!templateForm.value.file) {
    showNotification('Please select template image.', 'error')
    return
  }

  try {
    await uploadTemplate({
      name: templateForm.value.name,
      image: templateForm.value.file,
      is_default: templateForm.value.is_default,
    })

    templateForm.value = { name: '', file: null, is_default: false }
    showNotification('Template uploaded successfully.', 'success')
  } catch {
    showNotification('Failed to upload template.', 'error')
  }
}

const handleVerify = async () => {
  try {
    verifyResult.value = await $api.certificates.verifyByCode(verifyCode.value)
  } catch {
    verifyResult.value = { is_valid: false, message: 'Verification failed.' }
  }
}
</script>

<style scoped>
.head {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1rem;
}

.back-link {
  text-decoration: none;
  color: var(--brand-700);
  font-weight: 700;
}

.layout {
  display: grid;
  gap: 0.85rem;
  margin-top: 0.6rem;
}

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

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
  align-items: end;
}

.template-form,
.verify-form {
  display: grid;
  gap: 0.65rem;
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

.file-input {
  border: 1px solid var(--line-soft);
  border-radius: 10px;
  padding: 0.45rem;
  background: var(--background);
}

.check {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  font-size: 0.9rem;
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 0.65rem;
  margin-top: 0.65rem;
}

.template-card {
  background: color-mix(in srgb, var(--background) 92%, var(--muted));
}

.template-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
}

.preview {
  width: 100%;
  max-height: 220px;
  object-fit: contain;
  border-radius: 10px;
  border: 1px solid var(--line-soft);
  background: #fff;
}

.verify-result {
  margin-top: 0.75rem;
}

@media (max-width: 900px) {
  .head {
    flex-direction: column;
    align-items: flex-start;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
