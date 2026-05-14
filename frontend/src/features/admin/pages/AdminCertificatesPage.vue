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
        <AdminCreateCertificateCard
          :form="createForm"
          :user-options="userOptions"
          :tournament-options="tournamentOptions"
          :team-options="teamOptions"
          :template-options="templateOptions"
          :is-creating="isCreating"
          @update:form="createForm = $event"
          @submit="handleCreateCertificate"
        />

        <TemplateLibraryCard
          :template-form="templateForm"
          :is-uploading="isUploading"
          :is-templates-loading="isTemplatesLoading"
          :is-templates-error="isTemplatesError"
          :paginated-templates="paginatedTemplates"
          :templates-page="templatesPage"
          :total-template-pages="totalTemplatePages"
          @update:template-form="templateForm = $event"
          @file-change="onTemplateFileChange"
          @upload="handleUploadTemplate"
          @edit="openEdit"
          @delete="confirmDelete"
          @prev-page="prevTemplatePage"
          @next-page="nextTemplatePage"
        />

        <CertificateVerifyCard
          v-model:verify-code="verifyCode"
          :result="verifyResult"
          @submit="handleVerify"
        />

        <IssuedCertificatesCard
          v-model:search-query="searchQuery"
          v-model:certs-page="certsPage"
          :total-cert-pages="totalCertPages"
          :certs-response="certsResponse"
          :is-certs-loading="isCertsLoading"
          :is-certs-error="isCertsError"
          @search="handleSearch"
          @edit="openEditCert"
          @delete="confirmDeleteCert"
        />
      </div>
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

    <EditTemplateModal
      v-model="isEditModalOpen"
      :form="editForm"
      :is-updating="isUpdating"
      @update:form="editForm = $event"
      @file-change="onEditFileChange"
      @submit="handleUpdate"
    />

    <UiConfirmModal
      v-model="isDeleteCertModalOpen"
      title="Delete Certificate"
      message="Are you sure you want to delete this certificate? This action cannot be undone."
      confirmText="Delete"
      confirmVariant="danger"
      :loading="isDeletingCert"
      @confirm="onDeleteCertConfirm"
    />

    <EditCertificateModal
      v-model="isEditCertModalOpen"
      :form="editCertForm"
      :user-options="userOptions"
      :tournament-options="tournamentOptions"
      :team-options="teamOptions"
      :template-options="templateOptions"
      :is-updating="isUpdatingCert"
      @update:form="editCertForm = $event"
      @submit="handleUpdateCert"
    />
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiConfirmModal from '@/components/ui/UiConfirmModal.vue'
import { useUsers } from '@/api/queries/accounts'
import { useTeams } from '@/api/queries/teams'
import { useTournaments } from '@/api/queries/tournaments'
import {
  useCertificateTemplates,
  useCertificates,
  useCreateCertificate,
  useUploadCertificateTemplate,
  useUpdateCertificateTemplate,
  useDeleteCertificateTemplate,
  useUpdateCertificate,
  useDeleteCertificate,
} from '@/api/queries/certificates'
import { $api } from '@/api/services'
import { useNotification } from '@/composables/useNotification'
import AdminCreateCertificateCard from '@/features/admin/components/certificates/AdminCreateCertificateCard.vue'
import TemplateLibraryCard from '@/features/admin/components/certificates/TemplateLibraryCard.vue'
import CertificateVerifyCard from '@/features/admin/components/certificates/CertificateVerifyCard.vue'
import IssuedCertificatesCard from '@/features/admin/components/certificates/IssuedCertificatesCard.vue'
import EditTemplateModal from '@/features/admin/components/certificates/EditTemplateModal.vue'
import EditCertificateModal from '@/features/admin/components/certificates/EditCertificateModal.vue'

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

const { data: allTemplatesResponse } = useCertificateTemplates({ nopage: true })

const { mutateAsync: createCertificate, isPending: isCreating } = useCreateCertificate()
const { mutateAsync: uploadTemplate, isPending: isUploading } = useUploadCertificateTemplate()
const { mutateAsync: updateTemplate, isPending: isUpdating } = useUpdateCertificateTemplate()
const { mutateAsync: deleteTemplate, isPending: isDeleting } = useDeleteCertificateTemplate()

const isDeleteModalOpen = ref(false)
const templateToDeleteId = ref<number | null>(null)

const isEditModalOpen = ref(false)
const templateToEditId = ref<number | null>(null)
const editForm = ref({ name: '', file: null as File | null, is_default: false })

const certsPage = ref(1)
const certsPageSize = 10
const certsSearch = ref('')
const searchQuery = ref('')

const handleSearch = () => {
  certsSearch.value = searchQuery.value
  certsPage.value = 1
}

const {
  data: certsResponse,
  isLoading: isCertsLoading,
  isLoadingError: isCertsError,
} = useCertificates({ page: certsPage, pageSize: certsPageSize, search: certsSearch })

const { mutateAsync: updateCert, isPending: isUpdatingCert } = useUpdateCertificate()
const { mutateAsync: deleteCert, isPending: isDeletingCert } = useDeleteCertificate()

const isDeleteCertModalOpen = ref(false)
const certToDeleteCode = ref<string | null>(null)

const isEditCertModalOpen = ref(false)
const certToEditCode = ref<string | null>(null)
const editCertForm = ref({
  user: 0,
  tournament: 0,
  team: 0,
  template: 0,
  placement: '',
  certificate_number: '',
})

const totalCertPages = computed(() => {
  const total = certsResponse.value?.count || 0
  return Math.max(1, Math.ceil(total / certsPageSize))
})

const createForm = ref({
  user: 0,
  tournament: 0,
  team: 0,
  template: 0,
  placement: '',
  certificate_number: '',
})

const templateForm = ref({ name: '', file: null as File | null, is_default: false })
const verifyCode = ref('')
const verifyResult = ref<any>(null)

const userOptions = computed(() =>
  (users.value || []).map((u) => ({ value: u.id, label: `${u.full_name || u.username} (#${u.id})` })),
)

const tournamentOptions = computed(() =>
  (tournamentsResponse.value?.data || []).map((t) => ({ value: t.id, label: `${t.name} (#${t.id})` })),
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

const confirmDelete = (id: number) => {
  templateToDeleteId.value = id
  isDeleteModalOpen.value = true
}

const onDeleteConfirm = async () => {
  if (templateToDeleteId.value === null) return

  try {
    await deleteTemplate(templateToDeleteId.value)
    showNotification('Template deleted successfully.', 'success')
    isDeleteModalOpen.value = false
  } catch {
    showNotification('Failed to delete template.', 'error')
  }
}

const openEdit = (tpl: any) => {
  templateToEditId.value = tpl.id
  editForm.value = { name: tpl.name, file: null, is_default: tpl.is_default }
  isEditModalOpen.value = true
}

const onEditFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  editForm.value.file = target.files?.[0] || null
}

const handleUpdate = async () => {
  if (templateToEditId.value === null) return

  try {
    await updateTemplate({
      id: templateToEditId.value,
      data: {
        name: editForm.value.name,
        image: editForm.value.file || undefined,
        is_default: editForm.value.is_default,
      },
    })

    showNotification('Template updated successfully.', 'success')
    isEditModalOpen.value = false
  } catch {
    showNotification('Failed to update template.', 'error')
  }
}

const confirmDeleteCert = (code: string) => {
  certToDeleteCode.value = code
  isDeleteCertModalOpen.value = true
}

const onDeleteCertConfirm = async () => {
  if (!certToDeleteCode.value) return

  try {
    await deleteCert(certToDeleteCode.value)
    showNotification('Certificate deleted successfully.', 'success')
    isDeleteCertModalOpen.value = false
  } catch {
    showNotification('Failed to delete certificate.', 'error')
  }
}

const openEditCert = (cert: any) => {
  certToEditCode.value = cert.unique_code
  editCertForm.value = {
    user: cert.user,
    tournament: cert.tournament,
    team: cert.team || 0,
    template: cert.template || 0,
    placement: cert.placement,
    certificate_number: cert.certificate_number || '',
  }
  isEditCertModalOpen.value = true
}

const handleUpdateCert = async () => {
  if (!certToEditCode.value) return

  try {
    await updateCert({
      uniqueCode: certToEditCode.value,
      data: {
        user: editCertForm.value.user,
        tournament: editCertForm.value.tournament,
        team: editCertForm.value.team || null,
        template: editCertForm.value.template || null,
        placement: editCertForm.value.placement,
        certificate_number: editCertForm.value.certificate_number.trim() || undefined,
      },
    })
    showNotification('Certificate updated successfully.', 'success')
    isEditCertModalOpen.value = false
  } catch {
    showNotification('Failed to update certificate.', 'error')
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

@media (max-width: 900px) {
  .head {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
