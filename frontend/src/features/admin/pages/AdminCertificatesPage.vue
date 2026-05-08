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
          <ui-button as-link to="/admin/role-codes" variant="secondary">Back to admin panel</ui-button>
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
              <ui-input v-model="createForm.placement" required placeholder="1st" />
            </div>

            <div class="form-item">
              <label class="form-label">Certificate number (optional)</label>
              <ui-input v-model="createForm.certificate_number" placeholder="Leave empty for auto: CERT-YYYY-MM-DD" />
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
            <p v-else-if="!paginatedTemplates.length" class="text-muted">No templates uploaded yet.</p>

            <div v-else>
              <div class="templates-grid">
                <ui-card v-for="tpl in paginatedTemplates" :key="tpl.id" class="template-card">
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

              <div v-if="totalTemplatePages > 1" class="pagination">
                <ui-button size="sm" variant="secondary" :disabled="templatesPage === 1" @click="prevTemplatePage">Prev</ui-button>
                <span class="page-info">Page {{ templatesPage }} / {{ totalTemplatePages }}</span>
                <ui-button size="sm" variant="secondary" :disabled="templatesPage === totalTemplatePages" @click="nextTemplatePage">Next</ui-button>
              </div>
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
            <div class="input-wrap">
              <ui-input v-model="verifyCode" placeholder="Paste code or certificate number" required class="ui-input-full"/>
            </div>
            <ui-button class="verify-btn" type="submit">Verify</ui-button>
          </form>

          <div v-if="verifyResult" class="result" :class="verifyResult.is_valid ? 'result-valid' : 'result-invalid'">
            <div class="result-head">
              <p class="result-title">Verification result</p>
              <span class="status-badge" :class="verifyResult.is_valid ? 'status-valid' : 'status-invalid'">
                {{ verifyResult.is_valid ? 'Valid' : 'Invalid' }}
              </span>
            </div>

            <template v-if="verifyResult.data">
              <div class="result-grid">
                <p><span class="label">Name</span><strong>{{ verifyResult.data.full_name || '-' }}</strong></p>
                <p><span class="label">Team</span><strong>{{ verifyResult.data.team_name || '-' }}</strong></p>
                <p><span class="label">Tournament</span><strong>{{ verifyResult.data.tournament_name || '-' }}</strong></p>
                <p><span class="label">Certificate number</span><strong>{{ verifyResult.data.certificate_number || '-' }}</strong></p>
                <p><span class="label">Placement</span><strong>{{ verifyResult.data.placement || '-' }}</strong></p>
              </div>
            </template>

            <p v-if="verifyResult.message" class="result-message">{{ verifyResult.message }}</p>
          </div>
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

const templatesPage = ref(1)
const templatesPageSize = 8

// Paginated query for the Template Library
const {
  data: paginatedTemplatesResponse,
  isLoading: isTemplatesLoading,
  isLoadingError: isTemplatesError,
} = useCertificateTemplates({ page: templatesPage, pageSize: templatesPageSize })

const paginatedTemplates = computed(() => paginatedTemplatesResponse.value?.results || [])

const totalTemplatePages = computed(() => {
  const total = paginatedTemplatesResponse.value?.count || 0
  return Math.max(1, Math.ceil(total / templatesPageSize))
})

const prevTemplatePage = () => {
  if (templatesPage.value > 1) templatesPage.value -= 1
}

const nextTemplatePage = () => {
  if (templatesPage.value < totalTemplatePages.value) templatesPage.value += 1
}

// Unpaginated query for the Dropdown Options
const { data: allTemplatesResponse } = useCertificateTemplates({ nopage: true })

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
  ...(allTemplatesResponse.value?.results || []).map((t) => ({
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
      certificate_number: createForm.value.certificate_number.trim() || undefined,
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
    templatesPage.value = 1
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

.template-form {
  display: grid;
  gap: 0.65rem;
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
  border-radius: 12px;
  padding: 0.6rem 0.8rem;
  background: var(--background);
  color: var(--foreground);
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.file-input:hover {
  border-color: var(--primary);
}

.file-input::file-selector-button {
  background: var(--primary);
  color: var(--primary-foreground);
  border: none;
  border-radius: 8px;
  padding: 0.4rem 0.8rem;
  margin-right: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.file-input::file-selector-button:hover {
  opacity: 0.85;
}

.check {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  font-size: 0.9rem;
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
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

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-top: 16px;
}

.page-info {
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--color-gray-600);
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
