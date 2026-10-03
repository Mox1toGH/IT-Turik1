<template>
  <ui-card class="panel">
    <template #header>
      <div class="panel-head">
        <div class="panel-head-copy">
          <h2 class="panel-title">Template Library</h2>
          <p class="panel-note">Upload and preview certificate templates.</p>
        </div>
      </div>
    </template>

    <form class="template-form" @submit.prevent="submit">
      <div class="form-row">
        <div class="form-item">
          <label class="form-label">Template name</label>
          <ui-input v-model="form.name" required placeholder="Summer Cup 2026" />
        </div>

        <label class="check">
          <ui-switch v-model="form.is_default" />
          Make default template
        </label>
      </div>

      <div class="form-item">
        <label class="form-label">Image</label>
        <ui-file-drop
          v-model="form.files"
          accept="image/*"
          :multiple="false"
          hint="PNG, JPG or SVG"
        />
      </div>

      <ui-button type="submit" :disabled="isUploading" size="lg" class="submit">
        {{ isUploading ? 'Uploading...' : 'Upload Template' }}
      </ui-button>
    </form>

    <div class="panel-divider" aria-hidden="true"></div>

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
                <div class="template-info">
                  <strong>{{ tpl.name }}</strong>
                  <ui-badge :variant="tpl.is_default ? 'green' : 'gray'" class="status-badge-mini">
                    {{ tpl.is_default ? 'Default' : 'Template' }}
                  </ui-badge>
                </div>

                <div class="mini-actions">
                  <button
                    class="action-btn-mini"
                    title="Edit template"
                    @click.stop="handleEditTemplate(tpl)"
                  >
                    <EditIcon class="icon-mini" />
                  </button>
                  <button
                    class="action-btn-mini delete"
                    title="Delete template"
                    @click.stop="openDelete(tpl.id)"
                  >
                    <TrashIcon class="icon-mini" />
                  </button>
                </div>
              </div>
            </template>

            <img v-if="tpl.image_url" :src="tpl.image_url" :alt="tpl.name" class="preview" />
          </ui-card>
        </div>

        <ui-pagination
          v-if="totalTemplatePages > 1"
          v-model="templatesPage"
          :total-items="paginatedTemplates.length * totalTemplatePages"
          :page-size="paginatedTemplates.length"
          :show-summary="false"
        />
      </div>
    </ui-skeleton-loader>

    <EditTemplateModal :template="templateToEdit" v-model="isEditOpen" />
  </ui-card>

  <UiConfirmModal
    v-model="isDeleteModalOpen"
    title="Delete Template"
    message="Are you sure you want to delete this template? This action cannot be undone."
    confirmText="Delete"
    confirmVariant="danger"
    :loading="isDeleting"
    @confirm="onDeleteConfirm"
  />
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiPagination from '@/components/ui/UiPagination.vue'
import UiFileDrop from '@/components/ui/UiFileDrop.vue'
import UiSwitch from '@/components/ui/UiSwitch.vue'
import TrashIcon from '@/icons/TrashIcon.vue'
import EditIcon from '@/icons/EditIcon.vue'
import { useNotification } from '@/composables/useNotification'
import {
  useCreateCertificateTemplate,
  useDeleteCertificateTemplate,
  useListCertificateTemplates,
} from '@/api/certificates/certificates'
import type { CertificateTemplateResponse } from '@/api/backendAPINinja.schemas'
import EditTemplateModal from './EditTemplateModal.vue'
import UiConfirmModal from '@/components/ui/UiConfirmModal.vue'

const isDeleteModalOpen = ref(false)
const templateToDeleteId = ref<number | null>(null)

const openDelete = (templateId: CertificateTemplateResponse['id']) => {
  if (!Number.isInteger(templateId)) {
    showNotification('Unable to delete a template without an ID.', 'error')
    return
  }

  templateToDeleteId.value = templateId
  isDeleteModalOpen.value = true
}

const { mutateAsync: deleteTemplate, isPending: isDeleting } = useDeleteCertificateTemplate()

const onDeleteConfirm = async () => {
  if (templateToDeleteId.value === null) return

  try {
    await deleteTemplate({ templateId: templateToDeleteId.value })
    showNotification('Template deleted successfully.', 'success')
    isDeleteModalOpen.value = false
    templateToDeleteId.value = null
  } catch {
    showNotification('Failed to delete template.', 'error')
  }
}

const isEditOpen = ref(false)
const templateToEdit = ref<CertificateTemplateResponse>()

const templatesPage = ref(1)
const templatesPageSize = 8

const {
  data,
  isLoading: isTemplatesLoading,
  isLoadingError: isTemplatesError,
} = useListCertificateTemplates(
  computed(() => ({ page: templatesPage.value, page_size: templatesPageSize })),
)

const paginatedTemplates = computed(() => data.value?.items || [])
const totalTemplatePages = computed(() => {
  const total = data.value?.count || 0
  return Math.max(1, Math.ceil(total / templatesPageSize))
})

const { showNotification } = useNotification()
const { mutateAsync: uploadTemplate, isPending: isUploading } = useCreateCertificateTemplate()

const form = reactive({
  name: '',
  files: [] as File[],
  is_default: false,
})

async function submit() {
  if (!form.files[0]) {
    showNotification('Please select template image.', 'error')
    return
  }

  try {
    await uploadTemplate({
      data: {
        image: form.files[0],
      },
      params: { name: form.name, is_default: form.is_default },
    })

    form.name = ''
    form.files = []
    form.is_default = false

    showNotification('Template uploaded successfully.', 'success')
  } catch {
    showNotification('Failed to upload template.', 'error')
  }
}

function handleEditTemplate(template: CertificateTemplateResponse) {
  if (!Number.isInteger(template.id)) {
    showNotification('Unable to edit a template without an ID.', 'error')
    return
  }

  templateToEdit.value = template
  isEditOpen.value = true
}
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

.panel-head-copy {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.panel-title {
  margin: 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-weight: 800;
}

.panel-note {
  margin: 0;
  color: var(--muted-foreground);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
}

.template-form {
  display: grid;
  gap: 0.75rem;
}

.form-row {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.form-item {
  display: grid;
  gap: 0.4rem;
  flex: 1 1 220px;
}

.form-label {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--foreground);
}

.check {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  font-size: 0.9rem;
  white-space: nowrap;
}

.submit {
  width: fit-content;
}

.panel-divider {
  height: 1px;
  margin: 1.1rem 0;
  background: var(--line-soft);
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 0.85rem;
}

.template-card {
  background: color-mix(in srgb, var(--background) 92%, var(--muted));
}

.template-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.5rem;
}

.template-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
  min-width: 0;
}

.template-info strong {
  word-break: break-word;
  font-size: 0.95rem;
  line-height: 1.2;
  color: var(--foreground);
}

.status-badge-mini {
  width: fit-content;
  font-size: 10px;
  padding: 2px 8px;
}

.mini-actions {
  display: flex;
  align-items: center;
  gap: 2px;
  min-width: 44px;
}

.action-btn-mini {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 999px;
  background: transparent;
  color: var(--muted-foreground);
  cursor: pointer;
  transition:
    background-color 0.15s ease,
    color 0.15s ease;
}

.action-btn-mini:hover {
  background: color-mix(in srgb, var(--accent-strong) 12%, transparent);
  color: var(--accent-strong);
}

.action-btn-mini.delete:hover {
  background: color-mix(in srgb, var(--destructive) 12%, transparent);
  color: var(--destructive);
}

.icon-mini {
  width: 15px;
  height: 15px;
}

.preview {
  width: 100%;
  max-height: 220px;
  object-fit: contain;
  border-radius: 10px;
  border: 1px solid var(--line-soft);
  background: var(--background);
}

@media (max-width: 560px) {
  .form-row {
    flex-direction: column;
    align-items: stretch;
  }

  .check {
    white-space: normal;
  }
}
</style>
